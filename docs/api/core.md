# API 参考 · 精算核心

## actuarial_pilot.core.life_table

### `LifeTable`

加载生命表 CSV，提供 qx/lx/dx 查询。

```python
from actuarial_pilot.core.life_table import LifeTable

lt = LifeTable("data/life_tables/CLA2020_male.csv")
lt.qx(30, "M")      # 0.000855
lt.lx(30, "M")      # 99756
lt.dx(30, "M")      # 85
```

### `load_default_table`

快速加载默认 CLA2020 生命表（男/女）。

```python
from actuarial_pilot.core.life_table import load_default_table
lt = load_default_table("M")
```

## actuarial_pilot.core.pricing

### `net_single_premium`

趸交净保费。

```python
from actuarial_pilot.core.pricing import net_single_premium
nsp = net_single_premium(sum_assured=500_000, age=30, sex="M", term=20,
                         interest_rate=0.03, table=table, product="term")
```

### `level_premium`

均衡年缴净保费。

### `gross_premium`

毛保费（净保费 × (1 + 费用率 + 利润率)）。

## actuarial_pilot.core.reserve

### `prospective_reserve`

将来法责任准备金。

```python
v = prospective_reserve(sum_assured=500_000, age_at_issue=30, sex="M",
                         term=20, interest_rate=0.03, table=table,
                         annual_premium=premium, duration=5)
```

### `retrospective_reserve`

过去法责任准备金。

### `zillmer_reserve`

Zillmer 准备金（含初始费用扣除）。

## actuarial_pilot.core.sensitivity

### `sensitivity_analysis`

对一组扰动参数做敏感性分析。

```python
from actuarial_pilot.core.sensitivity import sensitivity_analysis
result = sensitivity_analysis(base_params, metric_fn, perturbations)
```

### `tornado_plot`

绘制龙卷风图，返回 PNG bytes。

## actuarial_pilot.core.annuity

### `annuity_immediate` / `annuity_due`

普通年金 / 期初付年金现值。

```python
from actuarial_pilot.core.annuity import annuity_immediate, annuity_due
a = annuity_immediate(rate=0.05, n=10)      # 7.72
ad = annuity_due(rate=0.05, n=10)           # 8.11
```

## actuarial_pilot.core.mortality_improvement

### `apply_mortality_improvement`

对未来某年的死亡率做改善修正。

```python
from actuarial_pilot.core.mortality_improvement import apply_mortality_improvement
future_qx = apply_mortality_improvement(table, 40, "M", years_forward=10)
```