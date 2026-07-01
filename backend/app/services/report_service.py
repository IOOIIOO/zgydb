"""报告生成服务：汇总四步数据→组装→LLM润色→存DB→生成PDF"""

import os
from datetime import datetime
from sqlmodel import Session, select
from app.models.personality import PersonalityResult
from app.models.ability import AbilityPortrait
from app.models.recommendation import RecommendationRecord
from app.models.trend import TrendAnalysis
from app.models.development import DevelopmentPath
from app.models.report import Report
from app.models.progress import UserProgress
from app.services.model_interface import polish_report_local
from app.config import settings


def generate(session: Session, user_id: int) -> dict:
    p = session.exec(select(PersonalityResult).where(PersonalityResult.user_id == user_id)).first()
    a = session.exec(select(AbilityPortrait).where(AbilityPortrait.user_id == user_id)).first()
    recs = session.exec(select(RecommendationRecord).where(RecommendationRecord.user_id == user_id)).all()
    t = session.exec(select(TrendAnalysis).where(TrendAnalysis.user_id == user_id)).first()
    dp = session.exec(select(DevelopmentPath).where(DevelopmentPath.user_id == user_id).order_by(DevelopmentPath.version.desc())).first()

    report_data = {
        "personality": _personality(p),
        "ability": _ability(a),
        "recommendations": [_rec(r) for r in recs],
        "trend": _trend(t),
        "path": _path(dp),
    }

    draft = _assemble_text(report_data)
    polished = polish_report_local(draft)
    report_data["polished"] = polished

    existing = session.exec(select(Report).where(Report.user_id == user_id)).all()
    version = len(existing) + 1

    # 先生成 PDF（失败时 pdf_path 为空，不影响 DB 写入）
    pdf_path = _generate_pdf(user_id, version, report_data)

    report = Report(
        user_id=user_id, report_data=report_data,
        pdf_path=pdf_path or "", version=version,
    )
    session.add(report)

    progress = session.exec(select(UserProgress).where(UserProgress.user_id == user_id)).first()
    if progress:
        progress.step5_completed = True
        progress.updated_at = datetime.utcnow()

    session.commit()
    session.refresh(report)

    return {"id": report.id, "version": version, "report_data": report_data, "pdf_path": report.pdf_path}


def get_history(session: Session, user_id: int) -> list[dict]:
    recs = session.exec(select(Report).where(Report.user_id == user_id).order_by(Report.created_at.desc())).all()
    return [{"id": r.id, "version": r.version, "created_at": r.created_at.isoformat() if r.created_at else ""} for r in recs]


def get_detail(session: Session, report_id: int) -> dict | None:
    r = session.get(Report, report_id)
    if not r: return None
    return {"id": r.id, "version": r.version, "report_data": r.report_data, "pdf_path": r.pdf_path}


def _personality(p): return {"type": p.personality_type, "intensity": p.intensity_level, "ei": p.ei_score, "sn": p.sn_score, "tf": p.tf_score, "jp": p.jp_score, "strengths": p.strengths, "weaknesses": p.weaknesses, "portrait": p.portrait_description} if p else None
def _ability(a): return {"education": a.education, "knowledge": a.knowledge_score, "tool": a.tool_score, "project": a.project_score, "logic": a.logic_label, "communication": a.communication_label, "cert": a.cert_competition_label, "learning": a.learning_label, "strengths": a.strengths, "weaknesses": a.weaknesses} if a else None
def _rec(r): return {"match_score": r.match_score, "reason": r.recommendation_reason}
def _trend(t): return {"trend_data": t.trend_data, "risk_warnings": t.risk_warnings, "sources": t.info_sources} if t else None
def _path(dp): return {"short": dp.short_term_path, "mid": dp.mid_term_path, "long": dp.long_term_path, "resources": dp.resource_list, "version": dp.version} if dp else None


def _assemble_text(d: dict) -> str:
    sections = []
    if d["personality"]:
        sections.append(f"【性格画像】\n人格类型：{d['personality']['type']}\n画像描述：{d['personality']['portrait']}")
    if d["ability"]:
        sections.append(f"【能力画像】\n学历：{d['ability']['education']}\n三维评分：知识{d['ability']['knowledge']} 工具{d['ability']['tool']} 项目{d['ability']['project']}")
    if d["recommendations"]:
        rec_text = "\n".join([f"- 匹配度{r['match_score']}分：{r['reason'][:100]}" for r in d["recommendations"][:5]])
        sections.append(f"【岗位推荐】\n{rec_text}")
    if d["trend"]:
        sections.append(f"【行业趋势】\n{d['trend']['trend_data'].get('overview','')}")
    if d["path"]:
        sections.append(f"【发展路径】\n短期：{d['path']['short'].get('goal','')}\n中期：{d['path']['mid'].get('goal','')}\n长期：{d['path']['long'].get('goal','')}")
    return "\n\n".join(sections)


def _fmt_personality(p: dict | None) -> str:
    if not p: return "暂无数据"
    return (
        f"人格类型：{p.get('type', '')}（强度 {p.get('intensity', '')}）\n"
        f"EI={p.get('ei', '')}  SN={p.get('sn', '')}  TF={p.get('tf', '')}  JP={p.get('jp', '')}\n"
        f"优势：{', '.join(p.get('strengths', []))}\n"
        f"短板：{', '.join(p.get('weaknesses', []))}\n"
        f"描述：{p.get('portrait', '')}"
    )

def _fmt_ability(a: dict | None) -> str:
    if not a: return "暂无数据"
    return (
        f"学历：{a.get('education', '')}\n"
        f"知识={a.get('knowledge', '')}  工具={a.get('tool', '')}  项目={a.get('project', '')}\n"
        f"逻辑={a.get('logic', '')}  沟通={a.get('communication', '')}  证书竞赛={a.get('cert', '')}  学习={a.get('learning', '')}\n"
        f"优势：{', '.join(a.get('strengths', []))}\n"
        f"短板：{', '.join(a.get('weaknesses', []))}"
    )

def _fmt_recommendations(recs: list | None) -> str:
    if not recs: return "暂无数据"
    lines = []
    for i, r in enumerate(recs[:10], 1):
        lines.append(f"{i}. 匹配度 {r.get('match_score', 0)}分 — {r.get('reason', '')[:120]}")
    return "\n".join(lines)

def _fmt_trend(t: dict | None) -> str:
    if not t: return "暂无数据"
    lines = []
    trends = (t.get("trend_data") or {}).get("trends", []) if isinstance(t.get("trend_data"), dict) else []
    for item in trends[:6]:
        lines.append(f"【{item.get('dimension', '')}】{item.get('content', '')}")
    if t.get("risk_warnings"):
        lines.append(f"\n风险提示：{'；'.join(t['risk_warnings'][:5])}")
    return "\n".join(lines) if lines else "暂无趋势数据"

def _fmt_path(dp: dict | None) -> str:
    if not dp: return "暂无数据"
    parts = []
    for label, key in [("短期", "short"), ("中期", "mid"), ("长期", "long")]:
        d = dp.get(key, {})
        if d:
            parts.append(f"【{label}】{d.get('duration', '')}\n目标：{d.get('goal', '')}\n技能：{', '.join(d.get('skills', []))}")
            if d.get('milestones'):
                parts[-1] += f"\n里程碑：{', '.join(d['milestones'])}"
            if d.get('directions'):
                parts[-1] += f"\n方向：{', '.join(d['directions'])}"
            if d.get('advanced_skills'):
                parts[-1] += f"\n高阶技能：{', '.join(d['advanced_skills'])}"
    return "\n\n".join(parts) if parts else "暂无发展路径数据"


def _generate_pdf(user_id: int, version: int, data: dict) -> str | None:
    """用ReportLab生成简体中文PDF。失败返回 None，不阻断主流程。"""
    try:
        from reportlab.pdfgen import canvas
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont

        pdf_dir = os.path.abspath(settings.REPORT_DIR)
        os.makedirs(pdf_dir, exist_ok=True)
        pdf_path = os.path.join(pdf_dir, f"report_{user_id}_v{version}.pdf")

        c = canvas.Canvas(pdf_path)
        # 尝试注册中文字体（Windows系统自带）
        font_registered = False
        for font_path in [
            "C:/Windows/Fonts/msyh.ttc",
            "C:/Windows/Fonts/simhei.ttf",
            "C:/Windows/Fonts/simsun.ttc",
        ]:
            if os.path.exists(font_path):
                try:
                    pdfmetrics.registerFont(TTFont("ChineseFont", font_path))
                    c.setFont("ChineseFont", 12)
                    font_registered = True
                    break
                except Exception:
                    continue

        if not font_registered:
            c.setFont("Helvetica", 10)

        y = 800
        c.drawString(50, y, f"职业规划综合报告 — 版本 {version}"); y -= 30

        sections = [
            ("性格画像", _fmt_personality(data.get("personality"))),
            ("能力画像", _fmt_ability(data.get("ability"))),
            ("岗位推荐", _fmt_recommendations(data.get("recommendations"))),
            ("行业趋势", _fmt_trend(data.get("trend"))),
            ("发展路径", _fmt_path(data.get("path"))),
        ]

        for title, text in sections:
            if y < 100:
                c.showPage()
                if font_registered: c.setFont("ChineseFont", 12)
                else: c.setFont("Helvetica", 10)
                y = 800
            c.drawString(50, y, f"--- {title} ---"); y -= 20
            for line in text.split("\n"):
                if y < 50:
                    c.showPage()
                    if font_registered: c.setFont("ChineseFont", 12)
                    else: c.setFont("Helvetica", 10)
                    y = 800
                c.drawString(60, y, line[:120]); y -= 16
            y -= 10

        c.save()
        return pdf_path
    except Exception as e:
        import logging
        logging.getLogger("career").warning(f"PDF生成失败 (user={user_id} v{version}): {e}")
        return None
