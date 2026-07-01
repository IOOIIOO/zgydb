"""趋势分析服务：调用联网搜索 + 写DB"""

from sqlmodel import Session, select
from app.models.trend import TrendAnalysis
from app.models.direction import Direction
from app.services.model_interface import search_trends


def analyze_trend(session: Session, user_id: int, direction_id: int, position_id: int | None) -> dict:
    direction = session.get(Direction, direction_id)
    name = direction.name if direction else "未知方向"

    trend_data = search_trends(name)

    # risk_warnings 和 info_sources 直接从 LLM 输出中取
    risk_warnings = trend_data.get("risk_warnings", [])

    info_sources = trend_data.get("resources", [])

    # 清旧数据写入新数据
    old = session.exec(select(TrendAnalysis).where(TrendAnalysis.user_id == user_id)).all()
    for o in old:
        session.delete(o)

    record = TrendAnalysis(
        user_id=user_id,
        direction_id=direction_id,
        position_id=position_id,
        trend_data=trend_data,
        risk_warnings=risk_warnings,
        info_sources=info_sources,
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
