"""命令行：敏感性分析示例。

运行方式（在项目根目录 ActuarialPilot 下执行）：
    python examples/example_sensitivity.py
"""

from __future__ import annotations

import sys
from pathlib import Path

# 保证直接运行本脚本时也能找到项目根目录下的 actuarial_pilot 包
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from actuarial_pilot.core.life_table import load_default_table
from actuarial_pilot.core.pricing import level_premium
from actuarial_pilot.core.sensitivity import (
    default_perturbations,
    sensitivity_analysis,
    tornado_plot,
)


def main() -> None:
    table = load_default_table("M")

    def metric(p):
        return level_premium(
            sum_assured=p["sum_assured"], age=p["age"], sex=p["sex"],
            term=p["term"], interest_rate=p["interest_rate"], table=table,
        )

    result = sensitivity_analysis(
        {"age": 30, "sex": "M", "sum_assured": 100_000, "term": 20, "interest_rate": 0.03},
        metric,
        default_perturbations(),
    )

    print(f"基准保费：¥{result.base_value:,.2f}\n")
    print(result.results.to_string(index=False))
    print("\n龙卷风图已保存至 demo_output/tornado.png")

    import os
    os.makedirs("demo_output", exist_ok=True)
    with open("demo_output/tornado.png", "wb") as f:
        f.write(tornado_plot(result))


if __name__ == "__main__":
    main()