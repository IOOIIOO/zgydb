"""发展路径路由"""
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.database import get_session
from app.routers.auth import _get_current_user
from app.models.progress import UserProgress
from app.schemas.development import DevelopmentRequest
from app.schemas.user import UserResponse
from app.services.development_service import generate_path

router = APIRouter()

def _check_step3(session: Session, user_id: int):
    progress = session.exec(select(UserProgress).where(UserProgress.user_id == user_id)).first()
    if not progress or not progress.step3_completed:
        raise HTTPException(status_code=400, detail="请先完成岗位推荐（第三步）")

@router.post("/generate")
def gen(body: DevelopmentRequest, current_user: UserResponse = Depends(_get_current_user), session: Session = Depends(get_session)):
    _check_step3(session, current_user.id)
    return generate_path(session, current_user.id, body.direction_id, body.position_id)

@router.post("/regenerate")
def regen(body: DevelopmentRequest, current_user: UserResponse = Depends(_get_current_user), session: Session = Depends(get_session)):
    _check_step3(session, current_user.id)
    return generate_path(session, current_user.id, body.direction_id, body.position_id)
