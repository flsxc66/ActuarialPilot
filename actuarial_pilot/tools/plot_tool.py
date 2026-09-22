"""图表工具：保费曲线 + 敏感性龙卷风图。"""

from __future__ import annotations

import base64
import io

import matplotlib.pyplot as plt
import numpy as np

from ..core.life_table import load_default_table
from ..core.pricing import level_premium
from ..core.sensitivity import sensitivity_analysis, tornado_plot
from .base import ap_tool


@ap_tool("plot_premium_curve")
def plot_premium_curve_tool(
    start_age: int = 20,
    end_age: int = 60,
    sex: str = "M",
    sum_assured: float = 100_000,
    term: int = 20,
    interest_rate: float = 0.03,
) -> str:
    """绘制"不同年龄的均衡保费曲线"，返回 base64 编码 PNG。

    适用场景：用户想看保费随年龄变化趋势时。
    """
    table = load_default_table(sex)
    ages = list(range(start_age, min(end_age + 1, 60)))
    premiums = [
        level_premium(sum_assured, a, sex, term, interest_rate, table)
        for a in ages
    ]

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(ages, premiums, "o-", color="#4F46E5", linewidth=2)
    ax.set_xlabel("投保年龄")
    ax.set_ylabel("均衡年缴保费（元）")
    ax.set_title(
        f"定期寿险均衡保费随年龄变化（{sex}，{sum_assured/10000:.0f}万保额，{term}年期，利率{interest_rate*100:.1f}%）"
    )
    ax.grid(alpha=0.3)

    # 解决中文字体
    try:
        ax.set_title(ax.get_title(), fontproperties="DejaVu Sans")
    except Exception:  # noqa: BLE001
        pass

    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=120, bbox_inches="tight")
    plt.close(fig)
    return base64.b64encode(buf.getvalue()).decode("ascii")


@ap_tool("plot_sensitivity_tornado")
def plot_sensitivity_tornado_tool(
    age: int = 30,
    sex: str = "M",
    sum_assured: float = 100_000,
    term: int = 20,
    interest_rate: float = 0.03,
) -> str:
    """绘制敏感性分析龙卷风图，返回 base64 编码 PNG。

    视觉约定：涨→红色，跌→绿色（中国股市惯例）。
    """
    table = load_default_table(sex)

    def metric(p):
        return level_premium(
            sum_assured=p["sum_assured"], age=p["age"], sex=p["sex"],
            term=p["term"], interest_rate=p["interest_rate"], table=table,
        )

    from ..core.sensitivity import default_perturbations

    result = sensitivity_analysis(
        {"age": age, "sex": sex, "sum_assured": sum_assured, "term": term, "interest_rate": interest_rate},
        metric,
        default_perturbations(),
    )
    png = tornado_plot(result, title=f"{sex}{age}岁 {term}年期定期寿险")
    return base64.b64encode(png).decode("ascii")