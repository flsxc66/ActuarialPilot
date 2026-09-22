"""Orchestrator：基于 LangGraph 的多 Agent 路由。"""

from __future__ import annotations

from typing import Literal

from langchain_core.messages import HumanMessage
from langgraph.graph import END, StateGraph
from typing_extensions import TypedDict

from .llm import get_llm
from .pricing_agent import PricingAgent
from .underwriting_agent import UnderwritingAgent
from ..utils.logger import get_logger

logger = get_logger("agents.orchestrator")


class AgentState(TypedDict):
    """Agent 状态。"""

    user_input: str
    intent: str
    output: str


class Orchestrator:
    """根据意图路由到对应 Agent。"""

    def __init__(self) -> None:
        self.llm = get_llm()
        self.pricing_agent = PricingAgent(llm=self.llm)
        self.underwriting_agent = UnderwritingAgent(llm=self.llm)
        self.graph = self._build_graph()

    # ========== 路由节点 ==========

    def _route_intent(self, state: AgentState) -> AgentState:
        """用 LLM 判断用户意图。"""
        classification_prompt = (
            "你是意图分类器。根据用户输入回复一个词：PricingAgent 或 UnderwritingAgent。\n"
            "- 定价/敏感性/准备金/死亡率查询 → PricingAgent\n"
            "- 条款/核保/法规/产品细节问答 → UnderwritingAgent\n\n"
            "用户输入：{input}\n"
            "只回复一个词，不要解释。"
        )
        try:
            resp = self.llm.invoke(classification_prompt.format(input=state["user_input"]))
            intent = resp.content.strip()
            if "Pricing" in intent:
                intent = "PricingAgent"
            elif "Underwriting" in intent:
                intent = "UnderwritingAgent"
            else:
                intent = "PricingAgent"  # fallback
        except Exception as e:  # noqa: BLE001
            logger.warning("意图分类失败：%s，回退到 PricingAgent", e)
            intent = "PricingAgent"
        state["intent"] = intent
        return state

    def _call_pricing(self, state: AgentState) -> AgentState:
        try:
            output = self.pricing_agent.run(state["user_input"])
        except Exception as e:  # noqa: BLE001
            output = f"定价 Agent 调用失败：{e}"
        state["output"] = output
        return state

    def _call_underwriting(self, state: AgentState) -> AgentState:
        try:
            output = self.underwriting_agent.run(state["user_input"])
        except Exception as e:  # noqa: BLE001
            output = f"核保 Agent 调用失败：{e}"
        state["output"] = output
        return state

    def _route_after_intent(self, state: AgentState) -> Literal["pricing", "underwriting"]:
        return "pricing" if state["intent"] == "PricingAgent" else "underwriting"

    # ========== 构建图 ==========

    def _build_graph(self) -> StateGraph:
        graph = StateGraph(AgentState)
        graph.add_node("route_intent", self._route_intent)
        graph.add_node("pricing", self._call_pricing)
        graph.add_node("underwriting", self._call_underwriting)

        graph.set_entry_point("route_intent")
        graph.add_conditional_edges(
            "route_intent",
            self._route_after_intent,
            {"pricing": "pricing", "underwriting": "underwriting"},
        )
        graph.add_edge("pricing", END)
        graph.add_edge("underwriting", END)

        return graph.compile()

    def run(self, user_input: str) -> dict:
        """路由并执行，返回 final state。"""
        result = self.graph.invoke({"user_input": user_input, "intent": "", "output": ""})
        return result