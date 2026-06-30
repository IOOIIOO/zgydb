"""
users 表 — 用户认证

调用场景：
- 注册/登录：写入/读取用户凭据
- 所有需登录接口：通过 user_id 关联用户数据
"""

from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(max_length=50, unique=True, index=True, description="用户名")
    email: str = Field(max_length=255, unique=True, index=True, description="邮箱")
    password_hash: str = Field(max_length=255, description="密码哈希(bcrypt)")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="注册时间")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="更新时间")
