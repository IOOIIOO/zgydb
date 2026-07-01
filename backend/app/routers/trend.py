"""趋势分析路由"""
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.database import get_session
from app.routers.auth import _get_current_user
from app.models.progress import UserProgress
from app.schemas.trend import TrendRequest
from app.schemas.user import UserResponse
from app.services.trend_service import analyze_trend

router = APIRouter()

@router.post("/analyze")
def analyze(body: TrendRequest, current_user: UserResponse = Depends(_get_current_user), session: Session = Depends(get_session)):
    progress = session.exec(select(UserProgress).where(UserProgress.user_id == current_user.id)).first()
    if not progress or not progress.step3_completed:
        raise HTTPException(status_code=400, detail="请先完成岗位推荐（第三步）")
    return analyze_trend(session, current_user.id, body.direction_id, body.position_id)
