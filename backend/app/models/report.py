"""
reports 表 — 综合报告

服务于：
- 3.6 报告生成：存储完整报告数据 + PDF 路径

调用场景：
- POST /api/v1/report/generate — 写入报告
- GET  /api/v1/report/list — 历史报告列表
- GET  /api/v1/report/:id — 报告详情
- GET  /api/v1/report/:id/pdf — 下载 PDF
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import Column, JSON
from sqlmodel import Field, SQLModel


class Report(SQLModel, table=True):
    __tablename__ = "reports"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True, description="归属用户")
    report_data: dict = Field(
        sa_column=Column(JSON), default_factory=dict, description="完整报告结构化数据"
    )
    pdf_path: Optional[str] = Field(
        default=None, max_length=500, nullable=True, description="PDF 文件存储路径"
    )
    version: int = Field(default=1, description="版本号")
    created_at: datetime = Field(default_factory=datetime.utcnow)
