"""能力评估服务：编排假数据调用链"""

from sqlmodel import Session

from app.models.ability import AbilityPortrait
from app.models.certificate import CertificateRecord
from app.models.competition import CompetitionRecord
from app.models.progress import UserProgress
from app.services.model_interface import (
    extract_from_pdf,
    extract_from_text,
    score_abilities,
    infer_soft_labels,
    classify_certificate,
    classify_competition,
)
from sqlmodel import select
from datetime import datetime


def process_resume_file(session: Session, user_id: int, file_bytes: bytes) -> dict:
    """上传简历 → 提取 → 分级 → 评分 → 标签"""
    raw = extract_from_pdf(file_bytes)
    return _build_portrait(session, user_id, raw)


def process_description(session: Session, user_id: int, text: str) -> dict:
    """文字描述 → 提取 → 分级 → 评分 → 标签"""
    raw = extract_from_text(text)
    return _build_portrait(session, user_id, raw)


def _build_portrait(session: Session, user_id: int, raw: dict) -> dict:
    """统一处理：证书竞赛分级 → 评分 → 标签 → 写入DB"""
    # 证书分级
    certificates = []
    for cert in raw.get("certificates", []):
        result = classify_certificate(cert.get("name", ""))
        certificates.append({**cert, **result})

    # 竞赛分级
    competitions = []
    for comp in raw.get("competitions", []):
        result = classify_competition(comp.get("name", ""))
        competitions.append({**comp, **result})

    # 三维度评分
    scores = score_abilities(raw.get("skills", []))

    # 四软标签
    labels = infer_soft_labels(raw.get("projects", []))

    # 优势短板
    strengths = _derive_strengths(scores, labels)
    weaknesses = _derive_weaknesses(scores, labels)

    # 先删子表记录（FK约束），再删父表
    old_certs = session.exec(
        select(CertificateRecord).where(CertificateRecord.user_id == user_id)
    ).all()
    for c in old_certs:
        session.delete(c)
    old_comps = session.exec(
        select(CompetitionRecord).where(CompetitionRecord.user_id == user_id)
    ).all()
    for c in old_comps:
        session.delete(c)
    existing = session.exec(
        select(AbilityPortrait).where(AbilityPortrait.user_id == user_id)
    ).first()
    if existing:
        session.delete(existing)
    session.flush()

    portrait = AbilityPortrait(
        user_id=user_id,
        education=raw.get("education", ""),
        knowledge_score=scores["knowledge_score"],
        tool_score=scores["tool_score"],
        project_score=scores["project_score"],
        scoring_basis=scores.get("scoring_basis", {}),
        logic_label=labels["logic_label"],
        communication_label=labels["communication_label"],
        cert_competition_label=labels["cert_competition_label"],
        learning_label=labels["learning_label"],
        label_inference_basis=labels.get("label_inference_basis", {}),
        strengths=strengths,
        weaknesses=weaknesses,
        raw_extracted_data=raw,
    )
    session.add(portrait)
    session.flush()

    # 写入证书记录
    for cert in certificates:
        session.add(CertificateRecord(
            user_id=user_id,
            ability_portrait_id=portrait.id,  # type: ignore[arg-type]
            certificate_name=cert.get("name", ""),
            level=cert.get("level", 5),
            level_name=cert.get("level_name", "其他"),
            score=cert.get("score", 1),
        ))

    # 写入竞赛记录
    for comp in competitions:
        session.add(CompetitionRecord(
            user_id=user_id,
            ability_portrait_id=portrait.id,  # type: ignore[arg-type]
            competition_name=comp.get("name", ""),
            level=comp.get("level", 4),
            level_name=comp.get("level_name", "校级"),
            bonus_score=comp.get("bonus_score", 2),
        ))

    # 更新进度
    progress = session.exec(
        select(UserProgress).where(UserProgress.user_id == user_id)
    ).first()
    if progress is None:
        progress = UserProgress(user_id=user_id)
        session.add(progress)
    progress.step2_completed = True
    if progress.current_step < 3:
        progress.current_step = 3
    progress.updated_at = datetime.utcnow()

    session.commit()

    return {
        "education": portrait.education,
        "knowledge_score": portrait.knowledge_score,
        "tool_score": portrait.tool_score,
        "project_score": portrait.project_score,
        "scoring_basis": portrait.scoring_basis,
        "logic_label": portrait.logic_label,
        "communication_label": portrait.communication_label,
        "cert_competition_label": portrait.cert_competition_label,
        "learning_label": portrait.learning_label,
        "label_inference_basis": portrait.label_inference_basis,
        "strengths": portrait.strengths,
        "weaknesses": portrait.weaknesses,
        "certificates": certificates,
        "competitions": competitions,
    }


def _derive_strengths(scores: dict, labels: dict) -> list[str]:
    s = []
    if scores.get("knowledge_score", 0) >= 70:
        s.append("专业知识储备扎实")
    if scores.get("tool_score", 0) >= 75:
        s.append("工具使用熟练，技术栈实用")
    if scores.get("project_score", 0) >= 60:
        s.append("具备一定的项目实践经验")
    if labels.get("learning_label") in ("较强", "强"):
        s.append("学习能力突出，能快速掌握新技术")
    if labels.get("logic_label") in ("良好", "优秀"):
        s.append("逻辑思维清晰，善于分析问题")
    if not s:
        s.append("具备基本的专业素养，有提升空间")
    return s


def _derive_weaknesses(scores: dict, labels: dict) -> list[str]:
    w = []
    if scores.get("knowledge_score", 100) < 70:
        w.append("专业知识深度有待加强")
    if scores.get("tool_score", 100) < 70:
        w.append("建议拓展更多实用工具和技能")
    if scores.get("project_score", 100) < 70:
        w.append("项目经验偏少，建议多参与实际项目")
    if labels.get("communication_label") in ("一般", "较弱"):
        w.append("沟通协作能力需要提升")
    if labels.get("cert_competition_label") not in ("较强", "突出"):
        w.append("证书和竞赛经历不够突出")
    if not w:
        w.append("注意保持现有优势，持续积累")
    return w
