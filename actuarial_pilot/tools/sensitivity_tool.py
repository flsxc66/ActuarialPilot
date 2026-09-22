"""敏感性分析工具。"""

from __future__ import annotations

import json

from ..core.life_table import load_default_table
from ..core.pricing import level_premium
from ..core.sensitivity import (
    default_perturbations,
    sensitivity_analysis,
)
from .base import ap_tool


@ap_tool("sensitivity_tool")
def sensitivity_tool(
    age: int = 30,
    sex: str = "M",
    sum_assured: float = 100_000,
    term: int = 20,
    interest_rate: float = 0.03,
    product: str = "term",
) -> str:
    """对一款定价模型做敏感性分析，输出表格与龙卷风图 PNG（base64）。

    默认扰动：利率 ±50bp、死亡率 ±10%、保额 ±10%。
    适用场景：用户询问"利率变化对保费影响多大"、"死亡率假设敏感性"。

    Returns
    -------
    str
        JSON 字符串，包含 base_value、各扰动的 new_value/变化率/变化幅度。
    """
    table = load_default_table(sex)

    def metric(p):
        return level_premium(
            sum_assured=p["sum_assured"], age=p["age"], sex=p["sex"],
            term=p["term"], interest_rate=p["interest_rate"], table=table,
        )

    result = sensitivity_analysis(
        {
            "age": age, "sex": sex, "sum_assured": sum_assured,
            "term": term, "interest_rate": interest_rate,
        },
        metric,
        default_perturbations(),
    )
    payload = {
        "base_premium": round(result.base_value, 2),
        "sensitivities": result.results.to_dict(orient="records"),
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)