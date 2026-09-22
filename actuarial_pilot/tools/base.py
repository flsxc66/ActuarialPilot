"""工具基类与统一封装。"""

from __future__ import annotations

from functools import wraps
from typing import Callable

from langchain_core.tools import tool

from ..utils.logger import get_logger

logger = get_logger("tools.base")


def ap_tool(name: str | None = None):
    """统一装饰器：打日志 + 包装 LangChain @tool。

    使用示例
    --------
    >>> @ap_tool("my_tool")
    >>> def my_function(x: int) -> int:
    ...     '''工具描述。'''
    ...     return x * 2
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger.info("调用工具: %s(%s)", name or func.__name__, kwargs)
            try:
                result = func(*args, **kwargs)
                logger.info("工具 %s 完成", name or func.__name__)
                return result
            except Exception as e:
                logger.exception("工具 %s 失败: %s", func.__name__, e)
                return {"error": str(e), "tool": func.__name__}

        # 同时挂 LangChain tool 装饰
        wrapped = tool(name or func.__name__)(wrapper)
        return wrapped

    return decorator