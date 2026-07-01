"""能力评估服务：pypdf 提取文字 → LM Studio 统一分析 → 写库"""

from io import BytesIO
from sqlmodel import Session, select
from datetime import datetime

from app.models.ability import AbilityPortrait
from app.models.certificate import CertificateRecord
from app.models.competition import CompetitionRecord
from app.models.progress import UserProgress
from app.services.real_models.unified_analyzer import analyze_resume


def process_resume_file(session: Session, user_id: int, file_bytes: bytes) -> dict:
    """上传简历 → pypdf 提取文字 → LM Studio 统一分析"""
    text = _extract_pdf_text(file_bytes)
    if not text.strip():
        # PDF 无文字时尝试多模态（保留原 bailian_llm 的图片通路）
        from app.services.model_interface import extract_from_pdf
        raw = extract_from_pdf(file_bytes)
        return _build_portrait(session, user_id, raw)

    result = analyze_resume(text)
    return _build_portrait(session, user_id, result)


def process_description(session: Session, user_id: int, text: str) -> dict:
    """文字描述 → LM Studio 统一分析"""
    result = analyze_resume(text)
    return _build_portrait(session, user_id, result)


def _extract_pdf_text(file_bytes: bytes) -> str:
    """pypdf 本地提取 PDF 文字"""
    try:
        from pypdf import PdfReader
        reader = PdfReader(BytesIO(file_bytes))
        parts = []
        for page in reader.pages:
            t = page.extract_text()
            if t:
                parts.append(t)
        return "\n".join(parts)
    except Exception:
        return ""


def _build_portrait(session: Session, user_id: int, result: dict) -> dict:
    """将统一分析结果写入数据库"""

    # cert_competition_label 从分类结果汇总
    certificates = result.get("certificates", [])
    competitions = result.get("competitions", [])

    cert_max_score = max((c.get("score", 1) for c in certificates), default=0)
    comp_max_bonus = max((c.get("bonus_score", 2) for c in competitions), default=0)
    combined = max(cert_max_score, comp_max_bonus)
    if combined >= 8:
        cert_competition_label = "突出"
    elif combined >= 5:
        cert_competition_label = "较强"
    elif combined >= 3:
        cert_competition_label = "中等"
    else:
        cert_competition_label = "一般"

    # 补充 label_inference_basis
    label_basis = result.get("label_inference_basis", {})
    if "cert_competition" not in label_basis:
        label_basis["cert_competition"] = (
            f"证书最高{cert_max_score}分，竞赛最高加{comp_max_bonus}分，综合评定为{cert_competition_label}"
        )

    # 优势短板：优先用 LLM 给出的，回退到规则推导
    strengths = result.get("strengths", [])
    weaknesses = result.get("weaknesses", [])
    if not strengths or not weaknesses:
        strengths = _derive_strengths(result, result)
        weaknesses = _derive_weaknesses(result, result)

    # 清理旧记录
    for c in session.exec(select(CertificateRecord).where(CertificateRecord.user_id == user_id)).all():
        session.delete(c)
    for c in session.exec(select(CompetitionRecord).where(CompetitionRecord.user_id == user_id)).all():
        session.delete(c)
    existing = session.exec(select(AbilityPortrait).where(AbilityPortrait.user_id == user_id)).first()
    if existing:
        session.delete(existing)
    session.flush()

    portrait = AbilityPortrait(
        user_id=user_id,
        education=result.get("education", ""),
        knowledge_score=result.get("knowledge_score", 50),
        tool_score=result.get("tool_score", 50),
        project_score=result.get("project_score", 50),
        scoring_basis=result.get("scoring_basis", {}),
        logic_label=result.get("logic_label", "一般"),
        communication_label=result.get("communication_label", "一般"),
        cert_competition_label=cert_competition_label,
        learning_label=result.get("learning_label", "一般"),
        label_inference_basis=label_basis,
        strengths=strengths,
        weaknesses=weaknesses,
        raw_extracted_data=result,
    )
    session.add(portrait)
    session.flush()

    for cert in certificates:
        session.add(CertificateRecord(
            user_id=user_id,
            ability_portrait_id=portrait.id,
            certificate_name=cert.get("name", ""),
            level=cert.get("level", 5),
            level_name=cert.get("level_name", "其他"),
            score=cert.get("score", 1),
        ))

    for comp in competitions:
        session.add(CompetitionRecord(
            user_id=user_id,
            ability_portrait_id=portrait.id,
            competition_name=comp.get("name", ""),
            level=comp.get("level", 4),
            level_name=comp.get("level_name", "校级"),
            bonus_score=comp.get("bonus_score", 2),
        ))

    # 更新进度
    progress = session.exec(select(UserProgress).where(UserProgress.user_id == user_id)).first()
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
