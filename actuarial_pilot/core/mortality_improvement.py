"""死亡率改善因子。

真实定价中，需要对未来死亡率做趋势改善修正。
本模块提供：
- 简化版 Lee-Carter 模型
- 按改善率逐年折算
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from .life_table import LifeTable, SexType


def lee_carter_simplified(
    base_qx: pd.Series,
    annual_improvement_rate: float = 0.015,
    years_forward: int = 20,
) -> pd.DataFrame:
    """简化版 Lee-Carter 模型。

    假设死亡率每年按 ``annual_improvement_rate`` 指数下降。
    公式：``q_x(t+k) = qx_x * exp(-k * log(1 + annual_improvement_rate))``
    """
    log_rate = np.log(1.0 + annual_improvement_rate)
    ages = base_qx.index.astype(int)
    rows = []
    for k in range(years_forward + 1):
        factor = np.exp(-k * log_rate)
        rows.append(
            pd.DataFrame(
                {
                    "age": ages,
                    "year_offset": k,
                    "qx": base_qx.values * factor,
                }
            )
        )
    return pd.concat(rows, ignore_index=True)


def apply_mortality_improvement(
    table: LifeTable,
    age: int,
    sex: SexType,
    years_forward: int = 0,
    annual_improvement_rate: float = 0.015,
) -> float:
    """返回 ``years_forward`` 年后的死亡率。"""
    base = table.qx(age, sex)
    return base * np.exp(-years_forward * np.log(1.0 + annual_improvement_rate))


def build_improved_table(
    table: LifeTable,
    annual_improvement_rate: float = 0.015,
    projection_years: int = 0,
) -> LifeTable:
    """构造一个新的 ``LifeTable``，其 qx 已按改善率向下修正。

    注意：返回的是**新实例**，不会修改原生命表。
    """
    new_table = LifeTable.__new__(LifeTable)
    new_table.name = f"{table.name}-improved-{projection_years}y"
    new_table.min_age = table.min_age
    new_table.max_age = table.max_age
    new_table.BASE_LX = table.BASE_LX
    factor = np.exp(-projection_years * np.log(1.0 + annual_improvement_rate))
    new_table._qx = {k: v * factor for k, v in table._qx.items()}
    new_table._ages = sorted(new_table._qx.keys())
    return new_table