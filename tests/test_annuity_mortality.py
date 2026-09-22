"""年金 + 死亡率改善测试。"""

from __future__ import annotations

from pathlib import Path

from actuarial_pilot.core.annuity import annuity_due, annuity_immediate
from actuarial_pilot.core.life_table import LifeTable
from actuarial_pilot.core.mortality_improvement import apply_mortality_improvement


def test_annuity_immediate_simple_case():
    """教材经典题：i=5%, n=10。a_angle_10| ≈ 7.7217。"""
    a = annuity_immediate(0.05, 10)
    assert abs(a - 7.7217) < 1e-3


def test_annuity_due_equals_immediate_times_one_plus_i():
    """ä_angle_n| = a_angle_n| × (1 + i)。"""
    rate = 0.05
    n = 10
    d = annuity_due(rate, n)
    i = annuity_immediate(rate, n)
    assert abs(d - i * (1 + rate)) < 1e-6


def test_mortality_improvement_lowers_qx():
    csv = Path(__file__).resolve().parent.parent / "data" / "life_tables" / "CLA2020_male.csv"
    table = LifeTable(csv)
    base = table.qx(40, "M")
    improved_10y = apply_mortality_improvement(table, 40, "M", years_forward=10)
    assert improved_10y < base