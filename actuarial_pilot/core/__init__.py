"""ActuarialPilot 精算核心引擎。

所有精算公式的纯 Python 实现，**无任何 LLM 依赖**。
公式实现基于经典教材：
- 《寿险精算数学》李秀芳
- 《Life Contingencies》Bowers et al.
- SOA FM / MLC 考试大纲
"""

from __future__ import annotations

from .life_table import LifeTable, load_default_table
from .pricing import (
    gross_premium,
    level_premium,
    net_single_premium,
)
from .reserve import (
    fpt_reserve,
    prospective_reserve,
    retrospective_reserve,
    zillmer_reserve,
)
from .sensitivity import (
    SensitivityResult,
    sensitivity_analysis,
    tornado_plot,
)
from .annuity import (
    annuity_due,
    annuity_immediate,
)
from .mortality_improvement import (
    apply_mortality_improvement,
    lee_carter_simplified,
)

__all__ = [
    "LifeTable",
    "load_default_table",
    "net_single_premium",
    "level_premium",
    "gross_premium",
    "prospective_reserve",
    "retrospective_reserve",
    "fpt_reserve",
    "zillmer_reserve",
    "SensitivityResult",
    "sensitivity_analysis",
    "tornado_plot",
    "annuity_immediate",
    "annuity_due",
    "apply_mortality_improvement",
    "lee_carter_simplified",
]