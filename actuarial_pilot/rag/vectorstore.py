"""向量库封装（Chroma）。"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings

from ..config import APP_CONFIG
from ..utils.logger import get_logger
from .embed import get_embedding

logger = get_logger("rag.vectorstore")


class ActuarialVectorStore:
    """精算知识库向量存储。"""

    def __init__(
        self,
        embedding: Embeddings | None = None,
        persist_dir: Path | None = None,
        collection_name: str = "actuarial_kb",
    ) -> None:
        self.persist_dir = Path(persist_dir or APP_CONFIG.vectorstore_dir)
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        self.embedding = embedding or get_embedding()
        self.collection_name = collection_name
        self._store: Chroma | None = None

    @property
    def store(self) -> Chroma:
        if self._store is None:
            self._store = Chroma(
                collection_name=self.collection_name,
                embedding_function=self.embedding,
                persist_directory=str(self.persist_dir),
            )
        return self._store

    def add_documents(self, docs: list[Document]) -> None:
        if not docs:
            return
        self.store.add_documents(docs)
        logger.info("已写入 %d 个 chunk 至 %s", len(docs), self.persist_dir)

    def similarity_search(self, query: str, k: int = 3, **kwargs: Any) -> list[Document]:
        return self.store.similarity_search(query, k=k, **kwargs)

    def similarity_search_with_score(
        self, query: str, k: int = 3, **kwargs: Any,
    ) -> list[tuple[Document, float]]:
        return self.store.similarity_search_with_score(query, k=k, **kwargs)

    def reset(self) -> None:
        """清空整个 collection。"""
        try:
            self.store.delete_collection()
        except Exception:  # noqa: BLE001
            pass
        self._store = None
        logger.warning("向量库 %s 已重置", self.collection_name)

    def count(self) -> int:
        try:
            return self.store._collection.count()  # noqa: SLF001
        except Exception:  # noqa: BLE001
            return 0