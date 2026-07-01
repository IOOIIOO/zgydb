"""
通用响应模型
"""

from typing import Generic, TypeVar
from pydantic import BaseModel

T = TypeVar("T")


class PaginatedData(BaseModel, Generic[T]):
    """分页响应数据"""

    items: list[T]           # 数据列表
    total: int               # 总记录数
    page: int                # 当前页码
    page_size: int           # 每页条数
