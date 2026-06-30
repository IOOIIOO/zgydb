"""
用户认证相关请求/响应模型
"""

from pydantic import BaseModel, EmailStr


class RegisterRequest(BaseModel):
    """注册请求"""
    username: str
    email: str
    password: str


class LoginRequest(BaseModel):
    """登录请求"""
    email: str
    password: str


class UserResponse(BaseModel):
    """用户信息响应"""
    id: int
    username: str
    email: str
    created_at: str

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """登录/注册返回的 Token"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
