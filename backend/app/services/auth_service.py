"""
认证服务：密码哈希、JWT 签发与验证
"""

from datetime import datetime, timedelta

import bcrypt
from jose import JWTError, jwt
from sqlmodel import Session, select

from app.config import settings
from app.models.user import User


def hash_password(password: str) -> str:
    """对密码做 bcrypt 哈希"""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    """验证明文密码与哈希是否匹配"""
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))


def create_access_token(user_id: int) -> str:
    """签发 JWT 访问令牌"""
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": str(user_id), "exp": expire}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> int | None:
    """解析 JWT 令牌，返回 user_id；无效或过期返回 None"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return int(payload["sub"])
    except (JWTError, ValueError, KeyError):
        return None


def get_user_by_email(session: Session, email: str) -> User | None:
    """按邮箱查用户"""
    return session.exec(select(User).where(User.email == email)).first()


def get_user_by_id(session: Session, user_id: int) -> User | None:
    """按 ID 查用户"""
    return session.get(User, user_id)


def register_user(session: Session, username: str, email: str, password: str) -> tuple[User | None, str | None]:
    """
    注册新用户。
    返回 (user, None) 表示成功，返回 (None, error_msg) 表示失败。
    """
    if get_user_by_email(session, email):
        return None, "该邮箱已被注册"

    # 检查用户名唯一性
    existing = session.exec(select(User).where(User.username == username)).first()
    if existing:
        return None, "该用户名已被使用"

    user = User(
        username=username,
        email=email,
        password_hash=hash_password(password),
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user, None
