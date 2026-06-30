"""趋势分析请求模型"""
from pydantic import BaseModel

class TrendRequest(BaseModel):
    direction_id: int
    position_id: int | None = None
