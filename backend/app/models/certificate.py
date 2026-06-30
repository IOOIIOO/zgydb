"""
certificate_records 表 — 证书记录

服务于：
- 3.3 能力评估-分级环节：分类模型判定证书档次，存储分数

调用场景：
- 能力评估时写入，能力画像详情页列表展示
- 证书分数越档校验（规则引擎）
"""

from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class CertificateRecord(SQLModel, table=True):
    __tablename__ = "certificate_records"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True, description="归属用户")
    ability_portrait_id: int = Field(foreign_key="ability_portraits.id", index=True, description="关联能力画像")
    certificate_name: str = Field(max_length=200, description="证书名称")
    level: int = Field(description="档次编号（分类模型判定）")
    level_name: str = Field(max_length=50, description="档次名称")
    score: int = Field(default=0, description="得分")
    created_at: datetime = Field(default_factory=datetime.utcnow)
