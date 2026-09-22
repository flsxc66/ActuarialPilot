"""敏感性分析测试。"""

from __future__ import annotations

from pathlib import Path

from actuarial_pilot.core.life_table import LifeTable
from actuarial_pilot.core.pricing import level_premium
from actuarial_pilot.core.sensitivity import (
    default_perturbations,
    sensitivity_analysis,
    tornado_plot,
)

# 项目根目录下的生命表（绝对路径，保证从任意目录运行 pytest 都能找到）
LIFE_TABLE_CSV = (
    Path(__file__).resolve().parent.parent / "data" / "life_tables" / "CLA2020_male.csv"
)


def test_sensitivity_returns_correct_shape():
    table = LifeTable(LIFE_TABLE_CSV)
    base_params = {
        "age": 30, "sex": "M", "sum_assured": 100_000, "term": 20,
        "interest_rate": 0.03, "table": table,
    }

    def metric(p):
        return level_premium(
            sum_assured=p["sum_assured"], age=p["age"], sex=p["sex"],
            term=p["term"], interest_rate=p["interest_rate"], table=p["table"],
        )

    result = sensitivity_analysis(base_params, metric, default_perturbations())
    assert len(result.results) == 6  # 6 个默认扰动
    assert "abs_change" in result.results.columns
    # 龙卷风图能渲染
    png = tornado_plot(result, title="test")
    assert len(png) > 0


def test_sensitivity_higher_rate_lowers_premium():
    table = LifeTable(LIFE_TABLE_CSV)

    def metric(p):
        return level_premium(
            sum_assured=p["sum"], age=p["age"], sex="M",
            term=p["term"], interest_rate=p["rate"], table=table,
        )

    result = sensitivity_analysis(
        {"age": 30, "sum": 100_000, "term": 20, "rate": 0.03},
        metric,
        [
            {"var": "rate", "label": "rate -1%", "new_value": 0.02},
            {"var": "rate", "label": "rate +1%", "new_value": 0.04},
        ],
    )
    rate_up = result.results[result.results["label"] == "rate +1%"]["new_value"].iloc[0]
    rate_down = result.results[result.results["label"] == "rate -1%"]["new_value"].iloc[0]
    assert rate_up < rate_down  # 利率↑ → 保费↓