"""
ability_portraits 表 — 能力画像

服务于：
- 3.3 能力评估：存储 3硬维度评分 + 4软维度标签 + 原始提取数据

调用场景：
- POST /api/v1/ability/upload-resume — 触发画像生成
- POST /api/v1/ability/describe — 触发画像生成
- GET  /api/v1/ability/portrait — 读取已有画像
- 岗位推荐时读取评分做匹配计算
- 报告生成时汇总引用
"""

from datetime import datetime
from typing import Optional, Dict, List

from sqlalchemy import Column, JSON
from sqlmodel import Field, SQLModel


class AbilityPortrait(SQLModel, table=True):
    __tablename__ = "ability_portraits"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", unique=True, index=True, description="归属用户（一对一）")
    education: str = Field(max_length=50, default="", description="学历")

    # 3硬维度评分（参与岗位匹配计算）
    knowledge_score: int = Field(default=0, description="知识维度评分(0-100)")
    tool_score: int = Field(default=0, description="工具维度评分(0-100)")
    project_score: int = Field(default=0, description="项目维度评分(0-100)")
    scoring_basis: Dict[str, str] = Field(
        sa_column=Column(JSON), default_factory=dict, description="三维度评分依据"
    )

    # 4软维度标签（不参与匹配公式，仅外围控制）
    logic_label: str = Field(max_length=50, default="", description="逻辑与解决问题标签")
    communication_label: str = Field(max_length=50, default="", description="沟通与协作标签")
    cert_competition_label: str = Field(max_length=50, default="", description="证书/竞赛含金量标签")
    learning_label: str = Field(max_length=50, default="", description="学习能力标签（后置微调系数）")
    label_inference_basis: Dict[str, str] = Field(
        sa_column=Column(JSON), default_factory=dict, description="四软维度标签推断依据"
    )

    # 汇总输出
    strengths: List[str] = Field(sa_column=Column(JSON), default_factory=list, description="优势清单")
    weaknesses: List[str] = Field(sa_column=Column(JSON), default_factory=list, description="短板清单")
    raw_extracted_data: dict = Field(
        sa_column=Column(JSON), default_factory=dict, description="原始提取的结构化数据"
    )

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
