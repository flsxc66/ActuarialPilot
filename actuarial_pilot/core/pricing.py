"""寿险定价引擎。

支持的险种：
- 定期寿险（Term Life）
- 终身寿险（Whole Life）
- 简易两全保险（Endowment）

输出：
- 趸交净保费（Net Single Premium, NSP）
- 均衡净保费（Level Annual Premium）
- 毛保费（Gross Premium，含费用与利润附加）
"""

from __future__ import annotations

from typing import Literal

import numpy as np

from .life_table import LifeTable, SexType

ProductType = Literal["term", "whole", "endowment"]


def _discount(rate: float, t: int) -> float:
    """贴现因子 v^t。"""
    return (1.0 + rate) ** (-t)


def net_single_premium(
    sum_assured: float,
    age: int,
    sex: SexType,
    term: int,
    interest_rate: float,
    table: LifeTable,
    product: ProductType = "term",
) -> float:
    """趸交净保费 (NSP)。

    数学公式
    ---------
    - 定期寿险： ``NSP = SA * sum_{t=0}^{term-1} v^{t+1} * {}_tp_x * q_{x+t}``
    - 终身寿险： ``NSP = SA * sum_{t=0}^{omega-x-1} v^{t+1} * {}_tp_x * q_{x+t}``
    - 两全保险： ``NSP = SA * (A_x:n| + v^n * {}_np_x)``

    Parameters
    ----------
    sum_assured : float
        保额（元）。
    age : int
        被保险人年龄。
    sex : SexType
        ``"M"`` / ``"F"``。
    term : int
        保险期限（终身寿险时设为 ``None``，由 ``product=whole`` 控制）。
    interest_rate : float
        年利率（小数，0.03 表示 3%）。
    table : LifeTable
        生命表实例。
    product : ProductType
        产品类型。

    Returns
    -------
    float
        趸交净保费（元）。
    """
    if product == "term":
        return _maturity_term_nsp(sum_assured, age, sex, term, interest_rate, table)
    if product == "whole":
        return _maturity_whole_nsp(sum_assured, age, sex, interest_rate, table)
    if product == "endowment":
        return _maturity_endowment_nsp(sum_assured, age, sex, term, interest_rate, table)
    raise ValueError(f"未知产品类型 {product}")


def level_premium(
    sum_assured: float,
    age: int,
    sex: SexType,
    term: int,
    interest_rate: float,
    table: LifeTable,
    product: ProductType = "term",
    payments_per_year: int = 1,
    payment_term: int | None = None,
) -> float:
    """均衡年缴净保费。

    数学公式
    ---------
    ``P = NSP / a_angle_x:n|``

    其中 ``ä_x:n|`` 是 n 年定期期初付年金现值。

    Parameters
    ----------
    payment_term : int | None
        缴费期限，``None`` 表示与保险期相同。
    """
    nsp = net_single_premium(
        sum_assured=sum_assured,
        age=age,
        sex=sex,
        term=term,
        interest_rate=interest_rate,
        table=table,
        product=product,
    )
    pay_n = payment_term if payment_term is not None else term
    annuity = annuity_factor(age, sex, pay_n, interest_rate, table, due=False)
    if annuity <= 0:
        raise ValueError("年金现值为 0，无法计算均衡保费")
    return nsp / annuity


def gross_premium(
    level_premium_value: float,
    expense_load: float = 0.05,
    profit_margin: float = 0.10,
) -> float:
    """毛保费 = 净保费 × (1 + 费用率 + 利润率)。

    Parameters
    ----------
    level_premium_value : float
        均衡净保费。
    expense_load : float
        费用率（默认 5%）。
    profit_margin : float
        利润率（默认 10%）。
    """
    return level_premium_value * (1.0 + expense_load + profit_margin)


def annuity_factor(
    age: int,
    sex: SexType,
    n: int,
    interest_rate: float,
    table: LifeTable,
    due: bool = False,
) -> float:
    """n 年定期生存年金现值。

    - 期末付（immediate）：``a_x:n| = sum_{t=1}^{n} v^t * {}_tp_x``
    - 期初付（due）：``ä_x:n| = a_x:n| + 1 - {}_np_x`` 的近似 -> ``= sum_{t=0}^{n-1} v^t * {}_tp_x``
    """
    if n <= 0:
        return 0.0
    v = lambda t: _discount(interest_rate, t)
    if due:
        return float(sum(v(t) * table.survival_factor(age, age + t, sex) for t in range(n)))
    return float(sum(v(t + 1) * table.survival_factor(age, age + t + 1, sex) for t in range(n)))


# ========== 内部辅助 ==========


def _maturity_term_nsp(
    sum_assured: float,
    age: int,
    sex: SexType,
    term: int,
    rate: float,
    table: LifeTable,
) -> float:
    """定期寿险趸交净保费 A1_x:n|。"""
    total = 0.0
    for t in range(term):
        prob = table.survival_factor(age, age + t, sex) * table.qx(age + t, sex)
        total += _discount(rate, t + 1) * prob
    return sum_assured * total


def _maturity_whole_nsp(
    sum_assured: float,
    age: int,
    sex: SexType,
    rate: float,
    table: LifeTable,
) -> float:
    """终身寿险趸交净保费 A_x。"""
    total = 0.0
    for t in range(table.max_age - age):
        if age + t >= table.max_age:
            break
        prob = table.survival_factor(age, age + t, sex) * table.qx(age + t, sex)
        total += _discount(rate, t + 1) * prob
    return sum_assured * total


def _maturity_endowment_nsp(
    sum_assured: float,
    age: int,
    sex: SexType,
    term: int,
    rate: float,
    table: LifeTable,
) -> float:
    """两全保险趸交净保费 A_x:n| + v^n * {}_np_x。"""
    death_benefit = _maturity_term_nsp(sum_assured, age, sex, term, rate, table)
    survival_benefit = sum_assured * _discount(rate, term) * table.survival_factor(age, age + term, sex)
    return death_benefit + survival_benefit