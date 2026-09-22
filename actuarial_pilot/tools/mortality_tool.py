"""生命表查询工具。"""

from __future__ import annotations

import json

from ..core.life_table import load_default_table
from .base import ap_tool


@ap_tool("mortality_tool")
def mortality_tool(
    age: int,
    sex: str = "M",
) -> str:
    """查询某年龄的死亡率 qx 和生存概率 px。

    适用场景：用户询问"30 岁男性的死亡率是多少"。
    """
    table = load_default_table(sex)
    qx = table.qx(age, sex)
    px = table.px(age, sex)
    lx = table.lx(age, sex)
    result = {
        "age": age,
        "sex": sex,
        "life_table": table.name,
        "qx": round(qx, 6),
        "qx_per_1000": round(qx * 1000, 3),
        "px": round(px, 6),
        "lx": lx,
        "interpretation": (
            f"{age} 岁{'男' if sex == 'M' else '女'}性当年死亡率 {qx*1000:.3f}‰，"
            f"即每千人中约 {qx*1000:.2f} 人预期在 1 年内身故。"
        ),
    }
    return json.dumps(result, ensure_ascii=False, indent=2)