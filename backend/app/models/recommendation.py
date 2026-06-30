"""
recommendation_records 表 — 岗位推荐记录

服务于：
- 3.4 岗位推荐：存储匹配结果和大模型撰写的推荐理由

调用场景：
- POST /api/v1/recommendation/recommend — 写入推荐记录
- 第四步推荐结果展示、报告引用
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import Column, Text
from sqlmodel import Field, SQLModel


class RecommendationRecord(SQLModel, table=True):
    __tablename__ = "recommendation_records"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True, description="归属用户")
    position_id: int = Field(foreign_key="positions.id", description="推荐的岗位")
    match_score: float = Field(default=0.0, description="匹配度（0-100）")
    recommendation_reason: str = Field(
        default="", sa_column=Column(Text), description="个性化推荐理由（大模型撰写）"
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)
