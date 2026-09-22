"""准备金评估测试。"""

from __future__ import annotations

from pathlib import Path

import pytest

from actuarial_pilot.core.life_table import LifeTable
from actuarial_pilot.core.pricing import level_premium
from actuarial_pilot.core.reserve import (
    fpt_reserve,
    prospective_reserve,
    retrospective_reserve,
    zillmer_reserve,
)


@pytest.fixture(scope="module")
def table() -> LifeTable:
    return LifeTable(
        Path(__file__).resolve().parent.parent / "data" / "life_tables" / "CLA2020_male.csv"
    )


@pytest.fixture(scope="module")
def annual_premium(table: LifeTable) -> float:
    return level_premium(100_000, 30, "M", 20, 0.03, table)


class TestReserve:
    def test_reserve_at_duration_zero_is_zero(self, table: LifeTable, annual_premium: float) -> None:
        v = prospective_reserve(
            100_000, 30, "M", 20, 0.03, table, annual_premium, duration=0,
        )
        assert v == 0.0

    def test_reserve_increases_with_duration(
        self, table: LifeTable, annual_premium: float,
    ) -> None:
        v1 = prospective_reserve(
            100_000, 30, "M", 20, 0.03, table, annual_premium, duration=5,
        )
        v10 = prospective_reserve(
            100_000, 30, "M", 20, 0.03, table, annual_premium, duration=15,
        )
        # 健康保单通常准备金单调递增
        assert v10 > v1

    def test_reserve_at_maturity(
        self, table: LifeTable, annual_premium: float,
    ) -> None:
        v = prospective_reserve(
            100_000, 30, "M", 20, 0.03, table, annual_premium, duration=20,
        )
        assert v == pytest.approx(0.0, abs=1e-6)

    def test_retrospective_positive_after_one_year(self, table: LifeTable) -> None:
        v = retrospective_reserve(
            annual_premium=500.0, age_at_issue=30, sex="M", term=20,
            interest_rate=0.03, table=table, duration=1,
        )
        assert v > 0

    def test_fpt_less_than_prospective_in_year_one(
        self, table: LifeTable, annual_premium: float,
    ) -> None:
        v_pros = prospective_reserve(
            100_000, 30, "M", 20, 0.03, table, annual_premium, duration=1,
        )
        v_fpt = fpt_reserve(
            100_000, 30, "M", 20, 0.03, table, annual_premium, duration=1,
        )
        # FPT 第一年不应高于将来法
        assert v_fpt <= v_pros + 1e-6

    def test_zillmer_less_than_prospective(
        self, table: LifeTable, annual_premium: float,
    ) -> None:
        v_pros = prospective_reserve(
            100_000, 30, "M", 20, 0.03, table, annual_premium, duration=5,
        )
        v_zill = zillmer_reserve(
            100_000, 30, "M", 20, 0.03, table, annual_premium,
            initial_expense=500.0, duration=5,
        )
        assert v_zill < v_pros