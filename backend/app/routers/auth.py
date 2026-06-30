"""
认证路由：注册、登录、获取当前用户

POST /api/v1/auth/register
POST /api/v1/auth/login
GET  /api/v1/auth/me
"""

from fastapi import APIRouter, Depends, HTTPException, Header
from sqlmodel import Session

from app.database import get_session
from app.schemas.user import LoginRequest, RegisterRequest, TokenResponse, UserResponse
from app.services.auth_service import (
    create_access_token,
    decode_access_token,
    get_user_by_id,
    register_user,
    verify_password,
)

router = APIRouter()


def _get_current_user(
    authorization: str = Header(description="Bearer <token>"),
    session: Session = Depends(get_session),
) -> UserResponse:
    """从请求头中提取并验证 JWT，返回当前用户"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="未提供有效的认证令牌")

    token = authorization[len("Bearer "):]
    user_id = decode_access_token(token)
    if user_id is None:
        raise HTTPException(status_code=401, detail="令牌无效或已过期")

    user = get_user_by_id(session, user_id)
    if user is None:
        raise HTTPException(status_code=401, detail="用户不存在")

    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        created_at=user.created_at.isoformat() if user.created_at else "",
    )


@router.post("/register", response_model=TokenResponse)
def register(body: RegisterRequest, session: Session = Depends(get_session)):
    """用户注册"""
    user, error = register_user(session, body.username, body.email, body.password)
    if error:
        raise HTTPException(status_code=400, detail=error)

    token = create_access_token(user.id)  # type: ignore[union-attr]
    return TokenResponse(
        access_token=token,
        user=UserResponse(
            id=user.id,  # type: ignore[union-attr]
            username=user.username,  # type: ignore[union-attr]
            email=user.email,  # type: ignore[union-attr]
            created_at=user.created_at.isoformat() if user.created_at else "",  # type: ignore[union-attr]
        ),
    )


@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest, session: Session = Depends(get_session)):
    """用户登录"""
    from app.services.auth_service import get_user_by_email

    user = get_user_by_email(session, body.email)
    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail="邮箱或密码错误")

    token = create_access_token(user.id)
    return TokenResponse(
        access_token=token,
        user=UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            created_at=user.created_at.isoformat() if user.created_at else "",
        ),
    )


@router.get("/me", response_model=UserResponse)
def me(current_user: UserResponse = Depends(_get_current_user)):
    """获取当前登录用户信息"""
    return current_user
