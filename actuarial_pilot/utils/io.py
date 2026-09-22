"""文件 IO 工具。"""

from __future__ import annotations

from pathlib import Path

import pandas as pd


def load_csv(path: str | Path, **kwargs) -> pd.DataFrame:
    """加载 CSV 文件，自动尝试 utf-8 / gbk 编码。"""
    path = Path(path)
    for enc in ("utf-8", "utf-8-sig", "gbk"):
        try:
            return pd.read_csv(path, encoding=enc, **kwargs)
        except UnicodeDecodeError:
            continue
    raise UnicodeDecodeError(f"无法以 utf-8/gbk 编码读取 {path}")


def save_csv(df: pd.DataFrame, path: str | Path, **kwargs) -> None:
    """保存 DataFrame 到 CSV。"""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, encoding="utf-8-sig", index=False, **kwargs)


def load_excel(path: str | Path, **kwargs) -> pd.DataFrame:
    """加载 Excel 文件。"""
    return pd.read_excel(path, **kwargs)


def save_excel(df: pd.DataFrame, path: str | Path, **kwargs) -> None:
    """保存 DataFrame 到 Excel。"""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_excel(path, index=False, **kwargs)