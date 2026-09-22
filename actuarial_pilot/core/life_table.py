"""生命表加载与查询。

生命表是精算的"字典"，本模块提供：
- 从 CSV 加载生命表
- 查询任意年龄的 qx / lx / dx
- 分数年龄插值（Uniform Distribution of Deaths, UDD）
"""

from __future__ import annotations

from pathlib import Path
from typing import Literal

import numpy as np
import pandas as pd

from ..config import APP_CONFIG
from ..utils.logger import get_logger

logger = get_logger("core.life_table")

SexType = Literal["M", "F"]


class LifeTable:
    """生命表类。

    Parameters
    ----------
    csv_path : str | Path
        生命表 CSV 文件路径，必须包含 ``age``、``sex``、``qx`` 三列。
    name : str
        生命表名称（用于日志与展示）。

    Examples
    --------
    >>> lt = LifeTable("data/life_tables/CLA2020_male.csv")
    >>> lt.qx(30, "M")
    0.000855
    >>> lt.lx(30, "M")
    99756
    """

    BASE_LX = 100_000  # 生命表基准生存人数

    def __init__(self, csv_path: str | Path, name: str = "CLA2020") -> None:
        self.name = name
        df = pd.read_csv(csv_path)
        if not {"age", "sex", "qx"}.issubset(df.columns):
            raise ValueError(f"生命表 {csv_path} 必须包含 age, sex, qx 三列")

        # 缓存：{("M"/"F", age): qx}
        self._qx: dict[tuple[SexType, int], float] = {
            (row.sex, int(row.age)): float(row.qx) for row in df.itertuples(index=False)
        }
        self._ages = sorted({a for (_, a) in self._qx})
        self.max_age = max(self._ages)
        self.min_age = min(self._ages)
        logger.info(
            "生命表 %s 加载完成：%s，%d-%d 岁，%d 行",
            name,
            csv_path,
            self.min_age,
            self.max_age,
            len(self._qx),
        )

    # ========== 基础查询 ==========

    def qx(self, age: int, sex: SexType, fractional: float = 0.0) -> float:
        """x 岁 + fractional 的死亡概率。

        分数年龄插值采用 UDD（Uniform Distribution of Deaths）：
        ``q_x+s = s * q_x``（0 ≤ s ≤ 1）
        """
        if not (self.min_age <= age <= self.max_age):
            raise ValueError(f"年龄 {age} 超出生命表范围 [{self.min_age}, {self.max_age}]")
        base_qx = self._qx[(sex, age)]
        if fractional <= 0:
            return base_qx
        if fractional >= 1:
            return 1.0
        return fractional * base_qx

    def px(self, age: int, sex: SexType) -> float:
        """生存概率：px = 1 - qx。"""
        return 1.0 - self.qx(age, sex)

    def lx(self, age: int, sex: SexType) -> int:
        """x 岁的生存人数（基准 l0 = 100,000）。

        采用递推公式 l_{x+1} = l_x * (1 - q_x)。
        """
        if age < self.min_age:
            age = self.min_age
        cur = self.BASE_LX
        for a in range(self.min_age, age):
            cur = int(round(cur * (1.0 - self._qx[(sex, a)])))
        return cur

    def dx(self, age: int, sex: SexType) -> int:
        """x → x+1 之间的死亡人数：d_x = l_x * q_x。"""
        return int(round(self.lx(age, sex) * self.qx(age, sex)))

    def get_table(self, sex: SexType) -> pd.DataFrame:
        """返回完整生命表（age, lx, dx, qx, px）。"""
        rows = []
        for age in range(self.min_age, self.max_age + 1):
            lx = self.lx(age, sex)
            dx = self.dx(age, sex)
            qx = self.qx(age, sex)
            rows.append({"age": age, "lx": lx, "dx": dx, "qx": qx, "px": 1 - qx})
        return pd.DataFrame(rows)

    # ========== 现值因子 ==========

    def discount_factor(self, years: float, rate: float) -> float:
        """贴现因子 v^t = (1 + i)^(-t)。"""
        return (1.0 + rate) ** (-years)

    def survival_factor(
        self,
        from_age: int,
        to_age: int,
        sex: SexType,
    ) -> float:
        """存活因子 {}_tp_x：x 岁活到 x+t 岁的概率。

        公式：{}_tp_x = prod_{k=0}^{t-1} p_{x+k}
        """
        if to_age <= from_age:
            return 1.0
        probs = [self.px(from_age + k, sex) for k in range(to_age - from_age)]
        return float(np.prod(probs))

    # ========== 分数年龄的现值 ==========

    def survival_factor_udd(
        self,
        from_age: int,
        to_age_with_fraction: float,
        sex: SexType,
    ) -> float:
        """存活因子（含分数年龄），采用 UDD 假设。"""
        from_age = int(from_age)
        to_full = int(np.floor(to_age_with_fraction))
        frac = to_age_with_fraction - to_full
        result = self.survival_factor(from_age, to_full, sex)
        if frac > 0:
            result *= 1.0 - self.qx(to_full, sex, fractional=frac)
        return result


def load_default_table(sex: SexType = "M") -> LifeTable:
    """加载默认生命表（CLA2020 男性/女性）。"""
    filename = "CLA2020_male.csv" if sex == "M" else "CLA2020_female.csv"
    path = APP_CONFIG.life_table_dir / filename
    return LifeTable(path, name=f"CLA2020-{sex}")