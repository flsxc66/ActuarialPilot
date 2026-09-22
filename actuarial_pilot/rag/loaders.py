"""文档加载器：支持 PDF / Markdown / TXT / HTML。"""

from __future__ import annotations

from pathlib import Path

from langchain_core.documents import Document
from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    UnstructuredMarkdownLoader,
)

from ..utils.logger import get_logger

logger = get_logger("rag.loaders")


def load_pdf(path: str | Path) -> list[Document]:
    loader = PyPDFLoader(str(path))
    docs = loader.load()
    for d in docs:
        d.metadata.setdefault("source", Path(path).name)
    logger.info("加载 PDF：%s，%d 页", path, len(docs))
    return docs


def load_markdown(path: str | Path) -> list[Document]:
    loader = UnstructuredMarkdownLoader(str(path))
    docs = loader.load()
    for d in docs:
        d.metadata.setdefault("source", Path(path).name)
    return docs


def load_text(path: str | Path) -> list[Document]:
    loader = TextLoader(str(path), encoding="utf-8")
    docs = loader.load()
    for d in docs:
        d.metadata.setdefault("source", Path(path).name)
    return docs


def load_documents(paths: list[str | Path]) -> list[Document]:
    """批量加载文档，根据后缀自动选择加载器。"""
    all_docs: list[Document] = []
    for p in paths:
        p = Path(p)
        if not p.exists():
            logger.warning("文件不存在：%s", p)
            continue
        suffix = p.suffix.lower()
        try:
            if suffix == ".pdf":
                all_docs.extend(load_pdf(p))
            elif suffix in (".md", ".markdown"):
                all_docs.extend(load_markdown(p))
            elif suffix in (".txt",):
                all_docs.extend(load_text(p))
            else:
                logger.warning("不支持的格式：%s", p)
        except Exception as e:  # noqa: BLE001
            logger.exception("加载失败：%s，%s", p, e)
    return all_docs