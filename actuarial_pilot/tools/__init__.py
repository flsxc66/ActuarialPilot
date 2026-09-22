"""Agent 可调用的工具层。"""

from __future__ import annotations

# 由于 RAG/Agents 包会反过来导入 tools 包里的某些工具，
# 我们直接在这里显式 import 并赋值，让包级名称指向具体工具对象。

from .pricing_tool import pricing_tool
from .sensitivity_tool import sensitivity_tool
from .reserve_tool import reserve_tool
from .mortality_tool import mortality_tool
from .plot_tool import plot_premium_curve_tool, plot_sensitivity_tornado_tool
from .search_tool import search_knowledge_base_tool
from .report_tool import generate_report_tool

__all__ = [
    "pricing_tool",
    "sensitivity_tool",
    "reserve_tool",
    "mortality_tool",
    "plot_premium_curve_tool",
    "plot_sensitivity_tornado_tool",
    "search_knowledge_base_tool",
    "generate_report_tool",
]