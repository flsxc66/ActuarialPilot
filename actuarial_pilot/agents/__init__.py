"""ActuarialPilot 智能体层。

- llm: 统一 LLM 工厂
- prompts: 中文 system prompt
- pricing_agent: 定价智能体
- underwriting_agent: 核保问答智能体
- orchestrator: 多 Agent 路由器（LangGraph 状态机）
- memory: 对话记忆

延迟导入说明：本包内模块互相引用 tools / rag，为避免循环导入，
本 __init__ 只暴露按需导入的接口。
"""

from __future__ import annotations

__all__ = [
    "get_llm",
    "PRICING_AGENT_PROMPT",
    "UNDERWRITING_AGENT_PROMPT",
    "ORCHESTRATOR_PROMPT",
    "PricingAgent",
    "UnderwritingAgent",
    "Orchestrator",
    "ConversationMemory",
]


def __getattr__(name: str):
    """延迟导入，避免循环依赖。"""
    if name == "get_llm":
        from .llm import get_llm

        return get_llm
    if name in ("PRICING_AGENT_PROMPT", "UNDERWRITING_AGENT_PROMPT", "ORCHESTRATOR_PROMPT"):
        from . import prompts

        return getattr(prompts, name)
    if name == "PricingAgent":
        from .pricing_agent import PricingAgent

        return PricingAgent
    if name == "UnderwritingAgent":
        from .underwriting_agent import UnderwritingAgent

        return UnderwritingAgent
    if name == "Orchestrator":
        from .orchestrator import Orchestrator

        return Orchestrator
    if name == "ConversationMemory":
        from .memory import ConversationMemory

        return ConversationMemory
    raise AttributeError(f"module 'actuarial_pilot.agents' has no attribute {name}")