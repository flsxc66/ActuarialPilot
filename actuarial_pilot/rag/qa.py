"""RAG 检索问答链。"""

from __future__ import annotations

import json
from pathlib import Path

from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI

from ..config import APP_CONFIG
from ..utils.logger import get_logger
from .loaders import load_documents
from .splitter import split_documents
from .vectorstore import ActuarialVectorStore

logger = get_logger("rag.qa")

QA_PROMPT = """你是保险条款与精算知识专家。请基于以下"参考资料"回答用户问题。

规则：
1. 只使用参考资料中的信息回答，不要凭训练数据回答。
2. 每条结论后用【来源: 文件名 页码】标注出处。
3. 如果参考资料中找不到答案，明确告诉用户"知识库中暂无该信息"。
4. 回答使用中文，专业、简洁、可审计。

参考资料：
{context}

用户问题：{question}

回答："""


class ActuarialQA:
    """RAG 检索问答。"""

    def __init__(
        self,
        vectorstore: ActuarialVectorStore | None = None,
        llm: ChatOpenAI | None = None,
    ) -> None:
        self.vs = vectorstore or ActuarialVectorStore()
        # 延迟导入避免循环
        if llm is None:
            from ..agents.llm import get_llm
            llm = get_llm()
        self.llm = llm
        self.prompt = ChatPromptTemplate.from_template(QA_PROMPT)
        self.parser = StrOutputParser()

    def ingest(self, file_paths: list[str | Path] | None = None) -> int:
        """把 data/policies + data/reports 下的文件入索引，返回 chunk 数。"""
        if file_paths is None:
            file_paths = []
            for d in (APP_CONFIG.policy_dir, APP_CONFIG.report_dir):
                if d.exists():
                    file_paths.extend([p for p in d.rglob("*") if p.is_file() and p.suffix.lower() in {".pdf", ".md", ".markdown", ".txt"}])
        if not file_paths:
            logger.warning("未发现可入库文件")
            return 0

        docs = load_documents(file_paths)
        chunks = split_documents(docs)
        self.vs.add_documents(chunks)
        return len(chunks)

    def ask(self, question: str, top_k: int = 3) -> dict:
        """检索 + 生成。"""
        try:
            retrieved: list[Document] = self.vs.similarity_search(question, k=top_k)
        except Exception as e:  # noqa: BLE001
            logger.exception("检索失败：%s", e)
            return {"answer": f"检索失败：{e}", "sources": []}

        context = "\n\n".join(_format_doc(d, i + 1) for i, d in enumerate(retrieved))
        chain = (
            {"context": RunnablePassthrough(), "question": RunnablePassthrough()}
            | self.prompt
            | self.llm
            | self.parser
        )
        answer = chain.invoke({"context": context, "question": question})

        sources = [
            {
                "name": d.metadata.get("source", "未知"),
                "page": d.metadata.get("page", "未知"),
                "snippet": d.page_content[:200],
            }
            for d in retrieved
        ]
        return {"answer": answer, "sources": sources}


def _format_doc(doc: Document, idx: int) -> str:
    src = doc.metadata.get("source", "未知")
    page = doc.metadata.get("page", "")
    return f"[{idx}] 来源: {src} {page}\n{doc.page_content}"


def get_default_qa() -> "ActuarialQA":
    """延迟初始化的默认 QA 实例。"""
    global _default_qa  # noqa: PLW0603
    if "_default_qa" not in globals() or _default_qa is None:
        _default_qa = ActuarialQA()
    return _default_qa


_default_qa: ActuarialQA | None = None