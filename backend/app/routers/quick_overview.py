"""
快速了解路由 — 无需登录，纯数据展示

GET /api/v1/overview/directions      → 方向列表
GET /api/v1/overview/directions/:id  → 方向详情
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.database import get_session
from app.models.direction import Direction
from app.schemas.direction import DirectionBrief, DirectionDetail

router = APIRouter()


@router.get("/directions", response_model=list[DirectionBrief])
def list_directions(session: Session = Depends(get_session)):
    """获取所有启用的方向，按 sort_order 排序"""
    stmt = (
        select(Direction)
        .where(Direction.is_active == True)
        .order_by(Direction.sort_order)
    )
    return session.exec(stmt).all()


@router.get("/directions/{direction_id}", response_model=DirectionDetail)
def get_direction(direction_id: int, session: Session = Depends(get_session)):
    """获取单个方向详情"""
    d = session.get(Direction, direction_id)
    if d is None or not d.is_active:
        raise HTTPException(status_code=404, detail="方向不存在")
    return d
