"""
通用响应模型

所有 API 接口统一使用此响应包装。
"""

from typing import Any, Generic, Optional, TypeVar
from pydantic import BaseModel

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    """统一 API 响应体"""

    code: int = 200          # 业务状态码，200 表示成功
    message: str = "success" # 提示信息
    data: Optional[T] = None # 响应数据


class PaginatedData(BaseModel, Generic[T]):
    """分页响应数据"""

    items: list[T]           # 数据列表
    total: int               # 总记录数
    page: int                # 当前页码
    page_size: int           # 每页条数
