"""责任准备金评估。

提供：
- 将来法（Prospective method）：``V = SA * A_{x+t:n-t|} - P * ä_{x+t:n-t|}``
- 过去法（Retrospective method）：``V = P * s_x:t - SA * (死亡给付已付总额)``
- FPT (Full Preliminary Term) 准备金
- Zillmer 准备金（含初始费用扣除）
"""

from __future__ import annotations

from typing import Literal

from .life_table import LifeTable, SexType
from .pricing import annuity_factor, net_single_premium


def prospective_reserve(
    sum_assured: float,
    age_at_issue: int,
    sex: SexType,
    term: int,
    interest_rate: float,
    table: LifeTable,
    annual_premium: float,
    duration: int = 1,
    product: Literal["term", "whole", "endowment"] = "term",
) -> float:
    """将来法责任准备金。

    公式
    ----
    在第 ``duration`` 保单年度末的责任准备金为：

    ``V = SA * A_{x+t:n-t|} - P * ä_{x+t:n-t|}``

    其中 t = duration, x+t = age_at_issue + duration。
    """
    if duration < 0 or duration > term:
        raise ValueError(f"评估时点 {duration} 超出保险期 {term}")
    age_now = age_at_issue + duration
    n_remaining = term - duration
    if n_remaining <= 0:
        return 0.0

    nsp = net_single_premium(
        sum_assured=sum_assured,
        age=age_now,
        sex=sex,
        term=n_remaining,
        interest_rate=interest_rate,
        table=table,
        product=product,
    )
    annuity = annuity_factor(age_now, sex, n_remaining, interest_rate, table, due=False)
    return nsp - annual_premium * annuity


def retrospective_reserve(
    annual_premium: float,
    age_at_issue: int,
    sex: SexType,
    term: int,
    interest_rate: float,
    table: LifeTable,
    duration: int = 1,
    sum_assured_paid: float = 0.0,
) -> float:
    """过去法责任准备金。

    公式
    ----
    ``V = P * s_x:t - SA * 已发生赔付与费用``

    此处采用简化版：忽略保额给付，只累算前期保费按利率复利。
    """
    if duration <= 0:
        return 0.0
    v = 1.0 + interest_rate
    accumulated_premium = annual_premium * sum(v ** (duration - k - 1) for k in range(duration))
    return accumulated_premium - sum_assured_paid


def fpt_reserve(
    sum_assured: float,
    age_at_issue: int,
    sex: SexType,
    term: int,
    interest_rate: float,
    table: LifeTable,
    annual_premium: float,
    duration: int,
) -> float:
    """FPT (Full Preliminary Term) 责任准备金。

    与将来法的区别：FPT 在最初 1 年内不允许持有正准备金，
    即将 P 用 NSP / a_angle_x:1| 替换。
    """
    if duration == 0:
        return 0.0
    # FPT 标准保费 = NSP / a_angle_x:1| (即第一年保费)
    nsp = net_single_premium(
        sum_assured=sum_assured,
        age=age_at_issue,
        sex=sex,
        term=term,
        interest_rate=interest_rate,
        table=table,
        product="term",
    )
    first_year_premium = nsp  # 简化：第一年保费 = NSP/1

    if duration == 1:
        # 第一年末按 FPT 保费与将来法计算
        v_after = prospective_reserve(
            sum_assured=sum_assured,
            age_at_issue=age_at_issue,
            sex=sex,
            term=term,
            interest_rate=interest_rate,
            table=table,
            annual_premium=first_year_premium,
            duration=1,
        )
        return v_after

    # 后续年度与将来法一致
    return prospective_reserve(
        sum_assured=sum_assured,
        age_at_issue=age_at_issue,
        sex=sex,
        term=term,
        interest_rate=interest_rate,
        table=table,
        annual_premium=annual_premium,
        duration=duration,
    )


def zillmer_reserve(
    sum_assured: float,
    age_at_issue: int,
    sex: SexType,
    term: int,
    interest_rate: float,
    table: LifeTable,
    annual_premium: float,
    initial_expense: float,
    duration: int = 1,
) -> float:
    """Zillmer 责任准备金（扣除初始费用）。"""
    base = prospective_reserve(
        sum_assured=sum_assured,
        age_at_issue=age_at_issue,
        sex=sex,
        term=term,
        interest_rate=interest_rate,
        table=table,
        annual_premium=annual_premium,
        duration=duration,
    )
    return base - initial_expense * (1.0 + interest_rate) ** (-duration)