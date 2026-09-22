"""文档切分：中文友好。"""

from __future__ import annotations

from langchain_core.documents import Document
from langchain_text_splitters import (
    MarkdownTextSplitter,
    RecursiveCharacterTextSplitter,
)

from ..utils.logger import get_logger

logger = get_logger("rag.splitter")


def split_documents(
    docs: list[Document],
    chunk_size: int = 500,
    chunk_overlap: int = 50,
) -> list[Document]:
    """按文档类型分别切分。"""
    markdown_docs = [d for d in docs if d.metadata.get("format", "").startswith("text/markdown") or d.metadata.get("source", "").endswith((".md", ".markdown"))]
    plain_docs = [d for d in docs if d not in markdown_docs]

    chunks: list[Document] = []

    if markdown_docs:
        md_splitter = MarkdownTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        chunks.extend(md_splitter.split_documents(markdown_docs))

    if plain_docs:
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", "。", "！", "？", "；", ". ", "! ", "? ", " ", ""],
        )
        chunks.extend(text_splitter.split_documents(plain_docs))

    logger.info("切分完成：%d 个文档 → %d 个 chunk", len(docs), len(chunks))
    return chunks