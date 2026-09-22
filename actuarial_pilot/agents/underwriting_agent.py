"""Underwriting Agent：基于 RAG 的核保问答。"""

from __future__ import annotations

from langchain_classic.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from .llm import get_llm
from .memory import ConversationMemory
from .prompts import UNDERWRITING_AGENT_PROMPT


class UnderwritingAgent:
    """核保问答 Agent（RAG-based）。"""

    def __init__(
        self,
        llm: BaseChatModel | None = None,
        memory: ConversationMemory | None = None,
    ) -> None:
        self.llm = llm or get_llm()
        self.memory = memory or ConversationMemory(session_id="underwriting")

        # 延迟导入避免循环
        from ..tools import search_knowledge_base_tool

        tools = [search_knowledge_base_tool]
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", UNDERWRITING_AGENT_PROMPT),
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
            max_iterations=3,
        )

    def run(self, user_input: str) -> str:
        self.memory.add("user", user_input)
        history = self.memory.get_history(limit=20)
        result = self.executor.invoke({"input": user_input, "chat_history": history})
        output = result.get("output", "")
        self.memory.add("assistant", output)
        return output