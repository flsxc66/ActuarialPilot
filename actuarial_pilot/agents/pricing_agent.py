"""Pricing Agent：对话式定价 + 敏感性 + 准备金。"""

from __future__ import annotations

from langchain_classic.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from .llm import get_llm
from .memory import ConversationMemory
from .prompts import PRICING_AGENT_PROMPT


class PricingAgent:
    """对话式精算 Agent。"""

    def __init__(
        self,
        llm: BaseChatModel | None = None,
        memory: ConversationMemory | None = None,
    ) -> None:
        self.llm = llm or get_llm()
        self.memory = memory or ConversationMemory(session_id="pricing")

        # 延迟导入避免循环
        from ..tools import (
            mortality_tool,
            plot_premium_curve_tool,
            plot_sensitivity_tornado_tool,
            pricing_tool,
            reserve_tool,
            sensitivity_tool,
        )

        tools = [
            pricing_tool,
            sensitivity_tool,
            reserve_tool,
            mortality_tool,
            plot_premium_curve_tool,
            plot_sensitivity_tornado_tool,
        ]

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", PRICING_AGENT_PROMPT),
                MessagesPlaceholder(variable_name="chat_history", optional=True),
                ("human", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ]
        )

        agent = create_tool_calling_agent(self.llm, tools, prompt)
        self.executor = AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=5,
        )

    def run(self, user_input: str) -> str:
        """单轮对话，返回自然语言回答。"""
        self.memory.add("user", user_input)
        history = self.memory.get_history(limit=20)
        result = self.executor.invoke({"input": user_input, "chat_history": history})
        output = result.get("output", "")
        self.memory.add("assistant", output)
        return output