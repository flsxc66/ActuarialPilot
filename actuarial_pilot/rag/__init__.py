"""RAG 知识库子系统（延迟导出，避免循环导入）。

组件：
- loaders: 加载 PDF / Markdown / HTML
- splitter: 中文友好切分
- embed: Embedding 工厂
- vectorstore: Chroma 封装
- qa: 检索问答链
"""

from __future__ import annotations

__all__ = [
    "load_documents",
    "split_documents",
    "get_embedding",
    "ActuarialVectorStore",
    "ActuarialQA",
    "get_default_qa",
]


def __getattr__(name: str):
    if name == "load_documents":
        from .loaders import load_documents

        return load_documents
    if name == "split_documents":
        from .splitter import split_documents

        return split_documents
    if name == "get_embedding":
        from .embed import get_embedding

        return get_embedding
    if name == "ActuarialVectorStore":
        from .vectorstore import ActuarialVectorStore

        return ActuarialVectorStore
    if name == "ActuarialQA":
        from .qa import ActuarialQA

        return ActuarialQA
    if name == "get_default_qa":
        from .qa import get_default_qa

        return get_default_qa
    raise AttributeError(f"module 'actuarial_pilot.rag' has no attribute {name}")