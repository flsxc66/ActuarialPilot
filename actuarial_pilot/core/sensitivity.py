"""敏感性分析框架。

支持对任意精算参数进行单因素扰动，返回敏感性表格 + 龙卷风图。
"""

from __future__ import annotations

import io
from dataclasses import dataclass
from typing import Callable, Iterable

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from ..utils.logger import get_logger

logger = get_logger("core.sensitivity")


@dataclass
class SensitivityResult:
    """敏感性分析结果。"""

    base_value: float
    results: pd.DataFrame  # 列：variable, perturbation, new_value, abs_change, pct_change
    tornado_png: bytes | None = None

    def to_markdown(self) -> str:
        """返回 Markdown 表格。"""
        return self.results.to_markdown(index=False, floatfmt=".4f")


def sensitivity_analysis(
    base_params: dict,
    metric_fn: Callable[[dict], float],
    perturbations: Iterable[dict],
) -> SensitivityResult:
    """对 base_params 应用扰动并计算 metric_fn 的差异。

    Parameters
    ----------
    base_params : dict
        基础参数，例如 ``{"age": 30, "sex": "M", "interest_rate": 0.03, ...}``。
    metric_fn : Callable[[dict], float]
        接受参数 dict，返回单个数值的函数。
    perturbations : Iterable[dict]
        每个扰动形如 ``{"var": "interest_rate", "label": "利率-50bp",
        "delta": -0.005, "new_value": None}``。
        - ``new_value`` 给定时直接覆盖；否则按 ``base + delta`` 计算。
    """
    base_value = float(metric_fn(base_params))
    rows = []
    for p in perturbations:
        new_params = dict(base_params)
        if p.get("new_value") is not None:
            new_params[p["var"]] = p["new_value"]
        elif p.get("relative", False):
            # 相对扰动：delta 表示比例，例如 -0.10 = -10%
            base = base_params.get(p["var"], 1.0)
            new_params[p["var"]] = base * (1.0 + p["delta"])
        else:
            # 绝对扰动：delta 表示加量
            base = base_params.get(p["var"], 0.0)
            new_params[p["var"]] = base + p["delta"]
        new_val = float(metric_fn(new_params))
        rows.append(
            {
                "variable": p["var"],
                "label": p.get("label", f'{p["var"]} {"+" if p.get("delta", 0) >= 0 else ""}{p.get("delta", 0)}'),
                "perturbation": p.get("delta", p.get("new_value")),
                "new_value": new_val,
                "abs_change": new_val - base_value,
                "pct_change": (new_val - base_value) / base_value if base_value != 0 else 0.0,
            }
        )
    df = pd.DataFrame(rows).sort_values("abs_change", key=lambda s: s.abs(), ascending=False)
    return SensitivityResult(base_value=base_value, results=df)


def tornado_plot(
    result: SensitivityResult,
    title: str = "敏感性分析 · 龙卷风图",
) -> bytes:
    """绘制龙卷风图（横向条形），返回 PNG bytes。

    视觉约定
    --------
    - 涨 → 红色（中国习惯）
    - 跌 → 绿色
    """
    df = result.results.copy()
    if df.empty:
        return b""

    fig, ax = plt.subplots(figsize=(9, max(3, 0.5 * len(df) + 1)))
    df["pct_pct"] = df["pct_change"] * 100
    colors = ["#E74C3C" if x >= 0 else "#27AE60" for x in df["pct_change"]]
    ax.barh(df["label"], df["pct_pct"], color=colors)
    ax.axvline(0, color="black", linewidth=0.8)
    ax.set_xlabel("变化率 (%)")
    ax.set_title(f"{title}｜基准={result.base_value:.2f}")
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=120, bbox_inches="tight")
    plt.close(fig)
    return buf.getvalue()


def default_perturbations() -> list[dict]:
    """默认扰动列表：利率±50bp、死亡率±10%、保额±10%。"""
    return [
        {"var": "interest_rate", "label": "利率 -50bp", "delta": -0.005},
        {"var": "interest_rate", "label": "利率 +50bp", "delta": 0.005},
        {"var": "mortality_factor", "label": "死亡率 -10%", "delta": -0.10},
        {"var": "mortality_factor", "label": "死亡率 +10%", "delta": 0.10},
        {"var": "sum_assured", "label": "保额 -10%", "delta": -0.10, "relative": True},
        {"var": "sum_assured", "label": "保额 +10%", "delta": 0.10, "relative": True},
    ]