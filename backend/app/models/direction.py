"""
directions 表 — 职业发展方向（静态数据）

服务于：
- 3.1 快速了解：方向列表 + 方向详情
- 第三步方向选择：用户选择一个方向
- 第四步性格约束过滤：排除不匹配的方向

调用场景：
- GET /api/v1/overview/directions — 快速了解列表
- GET /api/v1/overview/directions/:id — 快速了解详情
- GET /api/v1/recommendation/directions — 方向选择列表
- 岗位推荐时按 direction_id 筛选岗位
- 性格约束过滤时查询 excluded_personality_types
"""

from datetime import datetime
from typing import Optional, List

from sqlalchemy import Column, JSON, Text
from sqlmodel import Field, SQLModel


class Direction(SQLModel, table=True):
    __tablename__ = "directions"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=100, unique=True, description="方向名称")
    position_examples: List[str] = Field(
        sa_column=Column(JSON), default_factory=list, description="岗位举例列表"
    )
    required_skills: List[str] = Field(
        sa_column=Column(JSON), default_factory=list, description="所需能力与技术标签"
    )
    development_trend: str = Field(
        default="", sa_column=Column(Text), description="未来发展趋势描述"
    )
    excluded_personality_types: List[str] = Field(
        sa_column=Column(JSON), default_factory=list, description="排斥的人格类型列表"
    )
    excluded_trait_thresholds: dict = Field(
        sa_column=Column(JSON), default_factory=dict, description="排斥的极端特质阈值"
    )
    sort_order: int = Field(default=0, description="排序序号")
    is_active: bool = Field(default=True, description="是否启用")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
