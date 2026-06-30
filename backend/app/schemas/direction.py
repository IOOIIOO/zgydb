"""方向相关响应模型"""
from pydantic import BaseModel


class DirectionBrief(BaseModel):
    """方向列表项"""
    id: int
    name: str
    position_examples: list[str]
    sort_order: int

    class Config:
        from_attributes = True


class DirectionDetail(BaseModel):
    """方向详情"""
    id: int
    name: str
    position_examples: list[str]
    required_skills: list[str]
    development_trend: str

    class Config:
        from_attributes = True
