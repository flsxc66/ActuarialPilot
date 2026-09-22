"""ActuarialPilot · 对话式精算 Agent 工具箱。

一个面向寿险精算师的开源 AI Agent 工具箱，让用户用自然语言完成
产品定价、敏感性分析、责任准备金评估、条款问答等日常精算任务。

主要子包
--------
- :mod:`actuarial_pilot.core`     精算核心引擎（纯 Python，无 LLM 依赖）
- :mod:`actuarial_pilot.tools`    Agent 可调用的工具函数
- :mod:`actuarial_pilot.agents`   LangChain + LangGraph 智能体
- :mod:`actuarial_pilot.rag`      RAG 知识库子系统
- :mod:`actuarial_pilot.ui`       Streamlit Web UI
- :mod:`actuarial_pilot.utils`   通用工具函数
"""

from __future__ import annotations

__version__ = "0.1.0"
__author__ = "ActuarialPilot Contributors"
__license__ = "MIT"

__all__ = [
    "__version__",
    "__author__",
    "__license__",
]