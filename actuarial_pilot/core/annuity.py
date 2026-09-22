"""年金现值计算。

- 期末付年金（annuity-immediate）：``a_angle_n|``
- 期初付年金（annuity-due）：``ä_angle_n|``
- 终身年金 ``a_x`` 和 ``ä_x``
- 含生存概率的生命年金：``a_x:n|``
"""

from __future__ import annotations

from .life_table import LifeTable, SexType


def annuity_immediate(
    rate: float,
    n: int,
    table: LifeTable | None = None,
) -> float:
    """n 年期普通年金现值（不含生存概率）。

    公式：``a_angle_n| = (1 - v^n) / i``
    """
    if rate == 0:
        return float(n)
    v = 1.0 / (1.0 + rate)
    return (1.0 - v**n) / rate


def annuity_due(
    rate: float,
    n: int,
    table: LifeTable | None = None,
) -> float:
    """n 年期期初付年金现值。

    公式：``ä_angle_n| = (1 - v^n) / d``，d = i / (1+i)
    也等于 ``ä = a_angle_n| * (1 + i)``
    """
    if rate == 0:
        return float(n)
    d = rate / (1.0 + rate)
    v = 1.0 / (1.0 + rate)
    return (1.0 - v**n) / d


def life_annuity(
    age: int,
    sex: SexType,
    rate: float,
    table: LifeTable,
    due: bool = False,
) -> float:
    """终身生存年金现值 ``a_x`` 或 ``ä_x``。"""
    v = 1.0 / (1.0 + rate)
    total = 0.0
    if due:
        # 期初付：第一期立即支付
        total += 1.0
        start = 1
    else:
        start = 1
    for t in range(start, table.max_age - age + 1):
        prob = table.survival_factor(age, age + t, sex)
        if prob <= 0:
            break
        total += v**t * prob
    return total