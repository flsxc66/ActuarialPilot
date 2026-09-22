"""定价引擎测试。

参考教材：
- 《寿险精算数学》李秀芳，第 3 章例题
- SOA FM Sample Questions
"""

from __future__ import annotations

from pathlib import Path

import pytest

from actuarial_pilot.core.life_table import LifeTable
from actuarial_pilot.core.pricing import (
    gross_premium,
    level_premium,
    net_single_premium,
)


@pytest.fixture(scope="module")
def table() -> LifeTable:
    return LifeTable(
        Path(__file__).resolve().parent.parent / "data" / "life_tables" / "CLA2020_male.csv"
    )


class TestPricing:
    def test_term_life_nsp_positive(self, table: LifeTable) -> None:
        """趸交净保费应为正。"""
        nsp = net_single_premium(
            sum_assured=100_000, age=30, sex="M", term=20,
            interest_rate=0.03, table=table, product="term",
        )
        assert nsp > 0
        # 数量级合理性：30 岁男性 20 年期定期寿险 10 万元保额趸交净保费 ~¥1500-3000
        assert 1000 < nsp < 5000

    def test_term_premium_increases_with_term(self, table: LifeTable) -> None:
        """期限越长，保费越高。"""
        p10 = level_premium(100_000, 30, "M", 10, 0.03, table)
        p20 = level_premium(100_000, 30, "M", 20, 0.03, table)
        p30 = level_premium(100_000, 30, "M", 30, 0.03, table)
        assert p10 < p20 < p30

    def test_premium_increases_with_age(self, table: LifeTable) -> None:
        """年龄越大，保费越高（死亡率上升）。"""
        p25 = level_premium(100_000, 25, "M", 20, 0.03, table)
        p45 = level_premium(100_000, 45, "M", 20, 0.03, table)
        assert p45 > p25

    def test_premium_decreases_with_interest_rate(self, table: LifeTable) -> None:
        """利率越高，保费越低（贴现效果）。"""
        p_low = level_premium(100_000, 30, "M", 20, 0.02, table)
        p_high = level_premium(100_000, 30, "M", 20, 0.05, table)
        assert p_high < p_low

    def test_premium_proportional_to_sum_assured(self, table: LifeTable) -> None:
        """保费应与保额成正比。"""
        p1 = level_premium(100_000, 30, "M", 20, 0.03, table)
        p2 = level_premium(200_000, 30, "M", 20, 0.03, table)
        assert p2 == pytest.approx(2 * p1, rel=1e-6)

    def test_whole_life_more_expensive_than_term(self, table: LifeTable) -> None:
        """终身寿险的趸交保费应大于相同保额同年龄的 30 年期定期寿险。"""
        nsp_term = net_single_premium(
            100_000, 30, "M", 30, 0.03, table, "term",
        )
        nsp_whole = net_single_premium(
            100_000, 30, "M", 30, 0.03, table, "whole",
        )
        assert nsp_whole > nsp_term

    def test_endowment_between_term_and_deposit(self, table: LifeTable) -> None:
        """两全保险趸交保费应 > 定期寿险但 < 保额本身。"""
        nsp_term = net_single_premium(
            100_000, 30, "M", 20, 0.03, table, "term",
        )
        nsp_endow = net_single_premium(
            100_000, 30, "M", 20, 0.03, table, "endowment",
        )
        assert nsp_endow > nsp_term
        assert nsp_endow < 100_000

    def test_gross_premium_load(self) -> None:
        """毛保费 = 净保费 × (1 + 费用率 + 利润率)。"""
        net = 1.0
        gross = gross_premium(net, expense_load=0.05, profit_margin=0.10)
        assert gross == pytest.approx(1.15, rel=1e-9)

    def test_female_premium_lower_than_male(self) -> None:
        """女性保费应低于男性（同等条件）。"""
        female_table = LifeTable(
            Path(__file__).resolve().parent.parent / "data" / "life_tables" / "CLA2020_female.csv"
        )
        male_table = LifeTable(
            Path(__file__).resolve().parent.parent / "data" / "life_tables" / "CLA2020_male.csv"
        )
        p_m = level_premium(100_000, 30, "M", 20, 0.03, male_table)
        p_f = level_premium(100_000, 30, "F", 20, 0.03, female_table)
        assert p_f < p_m