"""命令行：RAG 问答示例。

运行方式（在项目根目录 ActuarialPilot 下执行）：
    python examples/example_rag.py
"""

from __future__ import annotations

import sys
from pathlib import Path

# 保证直接运行本脚本时也能找到项目根目录下的 actuarial_pilot 包
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from actuarial_pilot.rag.qa import ActuarialQA


def main() -> None:
    qa = ActuarialQA()
    qa.ingest(["data/policies/sample_term_life.md"])

    questions = [
        "犹豫期是几天？",
        "退保有损失吗？",
        "保单贷款最高能贷多少？",
    ]

    for q in questions:
        print(f"\n问：{q}")
        r = qa.ask(q, top_k=2)
        print(f"答：{r['answer']}")
        for src in r["sources"]:
            print(f"  - 来源：{src['name']} 第 {src['page']} 页")


if __name__ == "__main__":
    main()