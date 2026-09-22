"""Embedding 工厂。

支持：
- OpenAI 兼容接口（默认 DeepSeek）
- DashScope（通义千问）
- 本地 Sentence-Transformers（开发用，无需 API key）
"""

from __future__ import annotations

from langchain_core.embeddings import Embeddings

from ..config import EMBEDDING_CONFIG
from ..utils.logger import get_logger

logger = get_logger("rag.embed")


def get_embedding() -> Embeddings:
    """根据 EMBEDDING_PROVIDER 返回对应的 Embedding 实例。

    - ``"openai"``  → OpenAI 兼容接口
    - ``"dashscope"`` → DashScope
    - ``"local"``     → 本地 Sentence-Transformers（首次自动下载）
    """
    provider = EMBEDDING_CONFIG.provider.lower()

    if provider == "local":
        from langchain_community.embeddings import HuggingFaceEmbeddings

        logger.info("使用本地 Embedding 模型：paraphrase-multilingual-MiniLM-L12-v2")
        return HuggingFaceEmbeddings(
            model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )

    if provider == "dashscope":
        try:
            from langchain_community.embeddings import DashScopeEmbeddings
        except ImportError as e:
            raise ImportError("请先 `pip install dashscope`") from e
        return DashScopeEmbeddings(
            model=EMBEDDING_CONFIG.model,
            dashscope_api_key=EMBEDDING_CONFIG.api_key,
        )

    # 默认 OpenAI 兼容协议
    from langchain_openai import OpenAIEmbeddings

    return OpenAIEmbeddings(
        model=EMBEDDING_CONFIG.model,
        openai_api_key=EMBEDDING_CONFIG.api_key,
        openai_api_base=EMBEDDING_CONFIG.base_url,
    )