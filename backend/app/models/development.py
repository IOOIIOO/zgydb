"""
development_paths 表 — 发展路径

服务于：
- 3.5 发展路径：存储短/中/长期路径和建议资源

调用场景：
- POST /api/v1/development/generate — 写入路径
- POST /api/v1/development/regenerate — 版本+1重新生成
- 第四步路径Tab展示、报告引用
"""

from datetime import datetime
from typing import Optional, List

from sqlalchemy import Column, JSON
from sqlmodel import Field, SQLModel


class DevelopmentPath(SQLModel, table=True):
    __tablename__ = "development_paths"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True, description="归属用户")
    direction_id: int = Field(foreign_key="directions.id", description="关联方向")
    position_id: Optional[int] = Field(
        default=None, foreign_key="positions.id", nullable=True, description="关联岗位（可为空）"
    )

    short_term_path: dict = Field(
        sa_column=Column(JSON), default_factory=dict, description="短期路径（6月-1年）"
    )
    mid_term_path: dict = Field(
        sa_column=Column(JSON), default_factory=dict, description="中期路径（1-3年）"
    )
    long_term_path: dict = Field(
        sa_column=Column(JSON), default_factory=dict, description="长期路径（3-5年）"
    )
    resource_list: List[dict] = Field(
        sa_column=Column(JSON), default_factory=list, description="学习资源列表"
    )

    version: int = Field(default=1, description="版本号")
    created_at: datetime = Field(default_factory=datetime.utcnow)
