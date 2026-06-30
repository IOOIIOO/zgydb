"""
competition_records 表 — 竞赛记录

服务于：
- 3.3 能力评估-分级环节：分类模型判定竞赛级别，存储加分

调用场景：
- 能力评估时写入，能力画像详情页列表展示
"""

from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class CompetitionRecord(SQLModel, table=True):
    __tablename__ = "competition_records"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True, description="归属用户")
    ability_portrait_id: int = Field(foreign_key="ability_portraits.id", index=True, description="关联能力画像")
    competition_name: str = Field(max_length=200, description="竞赛名称")
    level: int = Field(description="级别编号（分类模型判定）")
    level_name: str = Field(max_length=50, description="级别名称")
    bonus_score: int = Field(default=0, description="加分")
    created_at: datetime = Field(default_factory=datetime.utcnow)
