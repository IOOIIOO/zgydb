"""
user_progress 表 — 用户流程进度

服务于：
- 全流程控制：严格按顺序完成 5 步，未完成上一步不能进入下一步

调用场景：
- Dashboard 页面加载时读取当前进度
- 每步完成后更新对应 stepN_completed 标记
- 第四步回退第三步时读取 selected_direction_id
"""

from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class UserProgress(SQLModel, table=True):
    __tablename__ = "user_progress"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", unique=True, index=True, description="归属用户（一对一）")
    current_step: int = Field(default=1, description="当前所在步骤(1-5)")

    step1_completed: bool = Field(default=False, description="性格分析是否完成")
    step2_completed: bool = Field(default=False, description="能力评估是否完成")
    step3_completed: bool = Field(default=False, description="方向选择是否完成")
    step4_completed: bool = Field(default=False, description="深度规划是否完成")
    step5_completed: bool = Field(default=False, description="报告生成是否完成")

    selected_direction_id: Optional[int] = Field(
        default=None,
        foreign_key="directions.id",
        nullable=True,
        description="第三步选中的方向ID",
    )

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
