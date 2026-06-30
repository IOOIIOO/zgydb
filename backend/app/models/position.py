"""
positions 表 — 岗位数据

服务于：
- 3.4 岗位推荐：基于能力画像匹配，返回推荐岗位列表

调用场景：
- POST /api/v1/recommendation/recommend — 返回匹配的岗位列表
- 学历硬门槛过滤时读取 education_requirement
- 性格约束过滤时读取 excluded_personality_types / excluded_trait_thresholds

数据来源：positions_cleaned.csv（智联招聘清洗后数据）
"""

from datetime import datetime
from typing import Optional, List

from sqlalchemy import Column, JSON, Text
from sqlmodel import Field, SQLModel


class Position(SQLModel, table=True):
    __tablename__ = "positions"

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(max_length=200, index=True, description="岗位标题")
    description: str = Field(
        default="", sa_column=Column(Text), description="岗位描述（HTML清洗后纯文本）"
    )
    direction_id: int = Field(
        foreign_key="directions.id", index=True, description="所属职业方向"
    )
    city: str = Field(
        max_length=50, default="", description="所在城市（用于前端筛选展示）"
    )
    industry: str = Field(
        max_length=200, default="", description="所属行业（用于趋势分析行业聚合）"
    )
    education_requirement: str = Field(
        max_length=50, default="本科", description="学历最低要求（用于学历硬门槛过滤）"
    )
    salary_range: str = Field(
        max_length=100, default="", description="薪资范围描述"
    )
    excluded_personality_types: List[str] = Field(
        sa_column=Column(JSON), default_factory=list, description="排斥的人格类型列表"
    )
    excluded_trait_thresholds: dict = Field(
        sa_column=Column(JSON), default_factory=dict, description="排斥的极端特质阈值"
    )
    is_active: bool = Field(default=True, description="是否启用")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
