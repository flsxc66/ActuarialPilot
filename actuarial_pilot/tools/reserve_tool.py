"""责任准备金工具。"""

from __future__ import annotations

import json

from ..core.life_table import load_default_table
from ..core.pricing import level_premium
from ..core.reserve import (
    prospective_reserve,
    retrospective_reserve,
    zillmer_reserve,
)
from .base import ap_tool


@ap_tool("reserve_tool")
def reserve_tool(
    age_at_issue: int = 30,
    sex: str = "M",
    sum_assured: float = 100_000,
    term: int = 20,
    interest_rate: float = 0.03,
    duration: int = 5,
    method: str = "prospective",
) -> str:
    """评估责任准备金。

    Parameters
    ----------
    method : str
        ``"prospective"`` 将来法 / ``"retrospective"`` 过去法 / ``"zillmer"`` 含初始费用扣除。
    duration : int
        评估时点（保单年度末）。
    """
    table = load_default_table(sex)
    annual_premium = level_premium(
        sum_assured=sum_assured, age=age_at_issue, sex=sex,
        term=term, interest_rate=interest_rate, table=table,
    )

    if method == "prospective":
        v = prospective_reserve(
            sum_assured, age_at_issue, sex, term, interest_rate,
            table, annual_premium, duration=duration,
        )
    elif method == "retrospective":
        v = retrospective_reserve(
            annual_premium, age_at_issue, sex, term,
            interest_rate, table, duration=duration,
        )
    elif method == "zillmer":
        v = zillmer_reserve(
            sum_assured, age_at_issue, sex, term, interest_rate,
            table, annual_premium, initial_expense=sum_assured * 0.01,
            duration=duration,
        )
    else:
        return json.dumps({"error": f"未知 method {method}"}, ensure_ascii=False)

    result = {
        "method": method,
        "duration": duration,
        "annual_premium": round(annual_premium, 2),
        "reserve": round(v, 2),
        "explanation": {
            "prospective": "将来法：未来给付现值 - 未来保费现值",
            "retrospective": "过去法：累计保费复利 - 累计已付赔付",
            "zillmer": "将来法 - 初始费用×折现因子",
        }[method],
    }
    return json.dumps(result, ensure_ascii=False, indent=2)