"""
trend_analyses 表 — 行业趋势分析

服务于：
- 3.5 行业趋势：存储针对用户+方向+岗位的完整趋势分析数据

调用场景：
- POST /api/v1/trend/analyze — 写入趋势分析
- 第四步趋势Tab展示、报告附录引用

趋势数据必须包含 6 个维度：
- 3-5年发展趋势、技术变革影响、地域需求差异
- 薪资走向、入门门槛变化、落到个体的分析
"""

from datetime import datetime
from typing import Optional, List

from sqlalchemy import Column, JSON
from sqlmodel import Field, SQLModel


class TrendAnalysis(SQLModel, table=True):
    __tablename__ = "trend_analyses"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True, description="归属用户")
    direction_id: int = Field(foreign_key="directions.id", description="分析的方向")
    position_id: Optional[int] = Field(
        default=None, foreign_key="positions.id", nullable=True, description="分析的岗位（可为空）"
    )
    trend_data: dict = Field(
        sa_column=Column(JSON), default_factory=dict, description="完整趋势数据（含6个必含维度）"
    )
    risk_warnings: List[str] = Field(
        sa_column=Column(JSON), default_factory=list, description="风险提示列表"
    )
    info_sources: List[dict] = Field(
        sa_column=Column(JSON), default_factory=list, description="信息来源列表"
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)
