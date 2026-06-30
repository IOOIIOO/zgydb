"""报告生成服务：汇总四步数据→组装→假数据润色→存DB→生成PDF"""

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
from app.services.model_interface import polish_report
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
    polished = polish_report(draft)

    existing = session.exec(select(Report).where(Report.user_id == user_id)).all()
    version = len(existing) + 1

    report = Report(
        user_id=user_id, report_data=report_data,
        pdf_path=f"reports/report_{user_id}_v{version}.pdf", version=version,
    )
    session.add(report)

    progress = session.exec(select(UserProgress).where(UserProgress.user_id == user_id)).first()
    if progress:
        progress.step5_completed = True
        progress.updated_at = datetime.utcnow()

    session.commit()
    session.refresh(report)

    # 生成PDF
    _generate_pdf(report.id, user_id, version, report_data)

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


def _generate_pdf(report_id: int, user_id: int, version: int, data: dict):
    """用ReportLab生成简体中文PDF"""
    try:
        from reportlab.pdfgen import canvas
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        import json

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
            ("性格画像", data.get("personality")),
            ("能力画像", data.get("ability")),
            ("岗位推荐", data.get("recommendations")),
            ("行业趋势", data.get("trend")),
            ("发展路径", data.get("path")),
        ]

        for title, content in sections:
            if y < 100:
                c.showPage()
                if font_registered: c.setFont("ChineseFont", 12)
                else: c.setFont("Helvetica", 10)
                y = 800
            c.drawString(50, y, f"--- {title} ---"); y -= 20
            text = json.dumps(content, ensure_ascii=False, indent=2) if content else "暂无数据"
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
    except Exception:
        return None
