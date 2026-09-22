"""命令行：定期寿险定价示例。

运行方式（在项目根目录 ActuarialPilot 下执行）：
    python examples/example_pricing.py
"""

from __future__ import annotations

import sys
from pathlib import Path

# 保证直接运行本脚本时也能找到项目根目录下的 actuarial_pilot 包
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from actuarial_pilot.core.life_table import load_default_table
from actuarial_pilot.core.pricing import (
    gross_premium,
    level_premium,
    net_single_premium,
)


def main() -> None:
    table = load_default_table("M")
    print(f"=== 已加载生命表：{table.name} ===\n")

    # 案例 1：30 岁男性 50 万保额 20 年期
    age, sex, sum_, term, rate = 30, "M", 500_000, 20, 0.03
    nsp = net_single_premium(sum_, age, sex, term, rate, table)
    net = level_premium(sum_, age, sex, term, rate, table)
    gross = gross_premium(net)
    print(f"[{age}岁{'男' if sex == 'M' else '女'} {sum_/10000:.0f}万 {term}年期 利率{rate*100:.1f}%]")
    print(f"  趸交净保费 = ¥{nsp:,.2f}")
    print(f"  均衡净保费 = ¥{net:,.2f}")
    print(f"  均衡毛保费 = ¥{gross:,.2f}\n")

    # 案例 2：女性，相同条件
    table_f = load_default_table("F")
    nsp_f = net_single_premium(sum_, age, "F", term, rate, table_f)
    net_f = level_premium(sum_, age, "F", term, rate, table_f)
    gross_f = gross_premium(net_f)
    print(f"[{age}岁女 {sum_/10000:.0f}万 {term}年期]")
    print(f"  趸交净保费 = ¥{nsp_f:,.2f}")
    print(f"  均衡净保费 = ¥{net_f:,.2f}")
    print(f"  均衡毛保费 = ¥{gross_f:,.2f}")
    print(f"  女 vs 男 保费比例 = {gross_f/gross:.2%}\n")

    # 案例 3：利率敏感性
    print("=== 利率敏感性（30岁男 50万 20年期）===")
    for r in (0.025, 0.03, 0.035, 0.04):
        p = level_premium(sum_, age, sex, term, r, table)
        print(f"  i={r*100:.1f}% → ¥{p:,.2f}")


if __name__ == "__main__":
    main()