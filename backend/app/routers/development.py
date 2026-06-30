"""发展路径路由"""
from fastapi import APIRouter, Depends
from sqlmodel import Session
from app.database import get_session
from app.routers.auth import _get_current_user
from app.schemas.development import DevelopmentRequest
from app.schemas.user import UserResponse
from app.services.development_service import generate_path

router = APIRouter()

@router.post("/generate")
def gen(body: DevelopmentRequest, current_user: UserResponse = Depends(_get_current_user), session: Session = Depends(get_session)):
    return generate_path(session, current_user.id, body.direction_id, body.position_id)

@router.post("/regenerate")
def regen(body: DevelopmentRequest, current_user: UserResponse = Depends(_get_current_user), session: Session = Depends(get_session)):
    return generate_path(session, current_user.id, body.direction_id, body.position_id)
