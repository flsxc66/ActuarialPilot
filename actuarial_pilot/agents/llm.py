"""LLM 工厂：统一 OpenAI 兼容协议，支持 DeepSeek / Qwen / OpenAI 等。"""

from __future__ import annotations

from functools import lru_cache

from langchain_openai import ChatOpenAI

from ..config import LLM_CONFIG
from ..utils.logger import get_logger

logger = get_logger("agents.llm")


@lru_cache(maxsize=1)
def get_llm() -> ChatOpenAI:
    """返回全局 LLM 实例（首次调用时创建，之后复用）。"""
    logger.info(
        "初始化 LLM: model=%s, base_url=%s",
        LLM_CONFIG.model,
        LLM_CONFIG.base_url,
    )
    return ChatOpenAI(
        model=LLM_CONFIG.model,
        api_key=LLM_CONFIG.api_key,
        base_url=LLM_CONFIG.base_url,
        temperature=LLM_CONFIG.temperature,
        max_tokens=LLM_CONFIG.max_tokens,
    )