"""
进度路由：查询用户流程进度

GET /api/v1/progress — 获取当前用户的 5 步完成状态
"""

from fastapi import APIRouter, Depends, HTTPException, Header
from sqlmodel import Session, select

from app.database import get_session
from app.models.progress import UserProgress
from app.services.auth_service import decode_access_token, get_user_by_id

router = APIRouter()


def _get_user_id(authorization: str = Header(description="Bearer <token>")) -> int:
    """从 JWT 提取 user_id，失败抛 401"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="未提供有效的认证令牌")
    token = authorization[len("Bearer "):]
    user_id = decode_access_token(token)
    if user_id is None:
        raise HTTPException(status_code=401, detail="令牌无效或已过期")
    return user_id


@router.get("")
def get_progress(
    authorization: str = Header(description="Bearer <token>"),
    session: Session = Depends(get_session),
):
    """获取当前用户流程进度"""
    user_id = _get_user_id(authorization)

    progress = session.exec(
        select(UserProgress).where(UserProgress.user_id == user_id)
    ).first()

    if progress is None:
        # 用户还没有任何进度记录，返回初始状态
        return {
            "current_step": 1,
            "step1_completed": False,
            "step2_completed": False,
            "step3_completed": False,
            "step4_completed": False,
            "step5_completed": False,
            "selected_direction_id": None,
        }

    return {
        "current_step": progress.current_step,
        "step1_completed": progress.step1_completed,
        "step2_completed": progress.step2_completed,
        "step3_completed": progress.step3_completed,
        "step4_completed": progress.step4_completed,
        "step5_completed": progress.step5_completed,
        "selected_direction_id": progress.selected_direction_id,
    }
