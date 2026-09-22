"""报告生成工具：把对话结果汇总为 Markdown 报告。"""

from __future__ import annotations

import json
from datetime import datetime

from .base import ap_tool


@ap_tool("generate_report")
def generate_report_tool(
    title: str,
    summary: str,
    sections: list[dict],
    format: str = "markdown",
) -> str:
    """生成精算报告（Markdown 或 JSON）。

    Parameters
    ----------
    title : str
        报告标题。
    summary : str
        一句话摘要。
    sections : list[dict]
        每节形如 ``{"heading": "...", "content": "..."}``。
    format : str
        ``"markdown"`` 或 ``"json"``。
    """
    if format == "markdown":
        lines = [
            f"# {title}",
            "",
            f"> **生成时间**：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"> **摘要**：{summary}",
            "",
        ]
        for i, sec in enumerate(sections, 1):
            lines.append(f"## {i}. {sec.get('heading', '')}")
            lines.append("")
            lines.append(sec.get("content", ""))
            lines.append("")
        return "\n".join(lines)
    return json.dumps({"title": title, "summary": summary, "sections": sections}, ensure_ascii=False, indent=2)