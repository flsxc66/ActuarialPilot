"""定价工具：LLM 可调用的产品定价函数。"""

from __future__ import annotations

import json
from typing import Literal

from ..core.life_table import load_default_table
from ..core.pricing import (
    gross_premium,
    level_premium,
    net_single_premium,
)
from .base import ap_tool

ProductType = Literal["term", "whole", "endowment"]
SexType = Literal["M", "F"]


@ap_tool("pricing_tool")
def pricing_tool(
    age: int,
    sex: SexType,
    sum_assured: float,
    term: int,
    interest_rate: float = 0.03,
    product: ProductType = "term",
    expense_load: float = 0.05,
    profit_margin: float = 0.10,
) -> str:
    """为寿险产品定价，返回 JSON 字符串。

    适用场景：用户询问"为 X 岁 Y 性别、Z 保额、W 年期的产品定个价"时调用。

    Parameters
    ----------
    age : int
        被保险人投保年龄（18-65）。
    sex : str
        性别，"M" 表示男性，"F" 表示女性。
    sum_assured : float
        保额（人民币元）。
    term : int
        保险期限（年数），终身寿险请用 100。
    interest_rate : float
        预定利率（年化，小数）。如 0.03 = 3%。
    product : str
        产品类型：``"term"`` 定期寿险 / ``"whole"`` 终身寿险 / ``"endowment"`` 两全险。
    expense_load : float
        费用率（小数），默认 5%。
    profit_margin : float
        利润率（小数），默认 10%。

    Returns
    -------
    str
        JSON 字符串，包含：
        - annual_premium: 均衡年缴毛保费
        - level_net_premium: 均衡净保费
        - net_single_premium: 趸交净保费
        - assumptions: 定价假设
        - formula_summary: 关键公式说明

    Examples
    --------
    >>> pricing_tool(30, "M", 500000, 20, 0.03)
    """
    if not 18 <= age <= 65:
        return json.dumps({"error": f"年龄 {age} 超出常见投保范围 18-65"}, ensure_ascii=False)
    if sum_assured <= 0 or term <= 0:
        return json.dumps({"error": "保额和保险期必须为正"}, ensure_ascii=False)

    table = load_default_table(sex)

    # 终身寿险特殊处理：term 用 100 表示
    if product == "whole":
        term = 100

    nsp = net_single_premium(
        sum_assured=sum_assured, age=age, sex=sex, term=term,
        interest_rate=interest_rate, table=table, product=product,
    )
    level_net = level_premium(
        sum_assured=sum_assured, age=age, sex=sex, term=term,
        interest_rate=interest_rate, table=table, product=product,
    )
    gross = gross_premium(level_net, expense_load, profit_margin)

    result = {
        "product": product,
        "params": {
            "age": age, "sex": sex, "sum_assured": sum_assured,
            "term": term, "interest_rate": interest_rate,
            "expense_load": expense_load, "profit_margin": profit_margin,
        },
        "results": {
            "net_single_premium": round(nsp, 2),
            "level_net_premium": round(level_net, 2),
            "annual_premium": round(gross, 2),
        },
        "assumptions": {
            "life_table": table.name,
            "interest_rate_pct": f"{interest_rate*100:.1f}%",
            "expense_load_pct": f"{expense_load*100:.1f}%",
            "profit_margin_pct": f"{profit_margin*100:.1f}%",
        },
        "formula_summary": {
            "nsp": "趸交净保费 = Σ v^(t+1) · t_p_x · q_{x+t}",
            "level_premium": "均衡保费 = NSP / a_angle_x:n|",
            "gross_premium": "毛保费 = 净保费 × (1 + 费用率 + 利润率)",
        },
    }
    return json.dumps(result, ensure_ascii=False, indent=2)