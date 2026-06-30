"""
personality_results 表 — 性格测评结果

服务于：
- 3.2 性格分析：存储 MBTI 测评结果，匹配 48 套描述模板

调用场景：
- POST /api/v1/personality/submit — 写入测评结果
- GET  /api/v1/personality/result — 读取已有结果
- 第三、四、五步参考性格数据
"""

from datetime import datetime
from typing import Optional, List

from sqlalchemy import Column, JSON, Text
from sqlmodel import Field, SQLModel


class PersonalityResult(SQLModel, table=True):
    __tablename__ = "personality_results"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", unique=True, index=True, description="归属用户")
    personality_type: str = Field(max_length=4, description="16型人格之一（如 INTJ）")
    intensity_level: int = Field(description="强度档：1弱/2中/3强")

    # 四维度得分
    ei_score: int = Field(default=0, description="E-I 维度得分")
    sn_score: int = Field(default=0, description="S-N 维度得分")
    tf_score: int = Field(default=0, description="T-F 维度得分")
    jp_score: int = Field(default=0, description="J-P 维度得分")

    # 匹配模板后的输出
    strengths: List[str] = Field(sa_column=Column(JSON), default_factory=list, description="长处列表")
    weaknesses: List[str] = Field(sa_column=Column(JSON), default_factory=list, description="短板列表")
    portrait_description: str = Field(
        default="", sa_column=Column(Text), description="综合画像描述（500-800字）"
    )
    direction_tendencies: List[str] = Field(
        sa_column=Column(JSON), default_factory=list, description="发展方向倾向列表"
    )

    created_at: datetime = Field(default_factory=datetime.utcnow, description="测评完成时间")
