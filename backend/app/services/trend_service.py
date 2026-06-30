"""趋势分析服务：调用 M3 假数据 + 写DB"""

from sqlmodel import Session, select
from app.models.trend import TrendAnalysis
from app.models.direction import Direction
from app.services.model_interface import search_trends


def analyze_trend(session: Session, user_id: int, direction_id: int, position_id: int | None) -> dict:
    direction = session.get(Direction, direction_id)
    name = direction.name if direction else "未知方向"

    trend_data = search_trends(name)

    # 清旧数据写入新数据
    old = session.exec(select(TrendAnalysis).where(TrendAnalysis.user_id == user_id)).all()
    for o in old:
        session.delete(o)

    record = TrendAnalysis(
        user_id=user_id,
        direction_id=direction_id,
        position_id=position_id,
        trend_data=trend_data,
        risk_warnings=["技术迭代快，需持续学习", "行业竞争加剧，建议差异化发展"],
        info_sources=[{"title": "行业研究报告", "url": "https://example.com/report"}],
    )
    session.add(record)
    session.commit()
    session.refresh(record)

    return {
        "id": record.id,
        "direction_id": direction_id,
        "trend_data": trend_data,
        "risk_warnings": record.risk_warnings,
        "info_sources": record.info_sources,
    }
