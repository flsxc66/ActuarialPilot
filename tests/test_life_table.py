"""生命表单元测试。"""

from __future__ import annotations

from pathlib import Path

import pytest

from actuarial_pilot.core.life_table import LifeTable, load_default_table


@pytest.fixture(scope="module")
def table() -> LifeTable:
    """整个测试 session 共享一个生命表实例。"""
    csv = Path(__file__).resolve().parent.parent / "data" / "life_tables" / "CLA2020_male.csv"
    return LifeTable(csv, name="CLA2020-M-test")


class TestLifeTable:
    def test_qx_at_key_ages(self, table: LifeTable) -> None:
        """关键年龄的 qx 应与 CSV 数据一致。"""
        assert table.qx(0, "M") == pytest.approx(0.000829, abs=1e-5)
        assert table.qx(30, "M") == pytest.approx(0.000855, abs=1e-4)
        assert table.qx(60, "M") == pytest.approx(0.005450, abs=1e-4)

    def test_px_equals_one_minus_qx(self, table: LifeTable) -> None:
        for age in [0, 20, 30, 50, 80]:
            assert table.px(age, "M") + table.qx(age, "M") == pytest.approx(1.0, abs=1e-9)

    def test_lx_is_monotone_decreasing(self, table: LifeTable) -> None:
        lxs = [table.lx(a, "M") for a in range(0, 100, 5)]
        assert all(a >= b for a, b in zip(lxs, lxs[1:], strict=False))

    def test_lx_base_value(self, table: LifeTable) -> None:
        assert table.lx(0, "M") == table.BASE_LX

    def test_dx_equals_lx_times_qx(self, table: LifeTable) -> None:
        for age in [0, 30, 60, 90]:
            expected = int(round(table.lx(age, "M") * table.qx(age, "M")))
            assert table.dx(age, "M") == expected

    def test_fractional_age_qx_uses_udd(self, table: LifeTable) -> None:
        """UDD：q_x+s = s * q_x。"""
        age, s = 30, 0.5
        expected = s * table.qx(age, "M")
        assert table.qx(age, "M", fractional=s) == pytest.approx(expected, abs=1e-7)

    def test_survival_factor_decreases_with_t(self, table: LifeTable) -> None:
        s1 = table.survival_factor(30, 50, "M")
        s2 = table.survival_factor(30, 70, "M")
        assert s1 > s2 > 0

    def test_load_default_table(self) -> None:
        lt_m = load_default_table("M")
        lt_f = load_default_table("F")
        assert lt_m.name.startswith("CLA2020")
        assert lt_f.name.startswith("CLA2020")
        assert lt_m.qx(30, "M") != lt_f.qx(30, "F")  # 男女表不一样

    def test_invalid_age_raises(self, table: LifeTable) -> None:
        with pytest.raises(ValueError):
            table.qx(table.max_age + 10, "M")
        with pytest.raises(ValueError):
            table.qx(-5, "M")