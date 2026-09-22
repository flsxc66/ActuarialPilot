"""RAG 检索工具。"""

from __future__ import annotations

import json

from .base import ap_tool


@ap_tool("search_knowledge_base")
def search_knowledge_base_tool(query: str, top_k: int = 3) -> str:
    """在知识库（保险条款 + 精算研报）中检索与 query 相关的内容。

    返回 JSON：包含 answer（带引用）、sources（来源文件名 + 页码）。

    适用场景：用户询问条款解读、监管规定、产品细节时。
    """
    # 延迟导入避免循环
    try:
        from ..rag.qa import ActuarialQA, get_default_qa

        qa = get_default_qa()
    except Exception:  # noqa: BLE001
        return json.dumps(
            {
                "warning": "知识库尚未初始化，请先在 Streamlit 侧边栏点击 '重建索引'。",
                "answer": "",
                "sources": [],
            },
            ensure_ascii=False,
        )

    result = qa.ask(query, top_k=top_k)
    return json.dumps(result, ensure_ascii=False, indent=2)