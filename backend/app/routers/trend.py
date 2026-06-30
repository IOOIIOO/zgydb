"""趋势分析路由"""
from fastapi import APIRouter, Depends
from sqlmodel import Session
from app.database import get_session
from app.routers.auth import _get_current_user
from app.schemas.trend import TrendRequest
from app.schemas.user import UserResponse
from app.services.trend_service import analyze_trend

router = APIRouter()

@router.post("/analyze")
def analyze(body: TrendRequest, current_user: UserResponse = Depends(_get_current_user), session: Session = Depends(get_session)):
    return analyze_trend(session, current_user.id, body.direction_id, body.position_id)
