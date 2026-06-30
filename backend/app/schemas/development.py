"""发展路径请求模型"""
from pydantic import BaseModel

class DevelopmentRequest(BaseModel):
    direction_id: int
    position_id: int | None = None
