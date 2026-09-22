"""ActuarialPilot 全局配置。

集中读取环境变量并对外暴露，方便在不依赖外部框架的前提下测试。
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

# 项目根目录（包所在目录的父级）
ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / ".env")


def _get_env(key: str, default: str | None = None) -> str:
    val = os.getenv(key, default)
    if val is None:
        raise RuntimeError(f"环境变量 {key} 未设置，且无默认值。请检查 .env 文件。")
    return val


@dataclass(frozen=True)
class LLMConfig:
    """LLM 相关配置（OpenAI 兼容协议）。"""

    api_key: str = field(default_factory=lambda: _get_env("OPENAI_API_KEY", ""))
    base_url: str = field(default_factory=lambda: _get_env("OPENAI_BASE_URL", "https://api.deepseek.com/v1"))
    model: str = field(default_factory=lambda: _get_env("OPENAI_MODEL", "deepseek-chat"))
    temperature: float = 0.0
    max_tokens: int = 2048


@dataclass(frozen=True)
class EmbeddingConfig:
    """Embedding 配置。"""

    provider: str = field(default_factory=lambda: _get_env("EMBEDDING_PROVIDER", "openai"))
    api_key: str = field(default_factory=lambda: _get_env("EMBEDDING_API_KEY", ""))
    base_url: str = field(default_factory=lambda: _get_env("EMBEDDING_BASE_URL", "https://api.deepseek.com/v1"))
    model: str = field(default_factory=lambda: _get_env("EMBEDDING_MODEL", "text-embedding-3-small"))


@dataclass(frozen=True)
class AppConfig:
    """ActuarialPilot 业务路径配置。"""

    life_table_dir: Path = field(default_factory=lambda: Path(_get_env("AP_LIFE_TABLE_DIR", "./data/life_tables")))
    policy_dir: Path = field(default_factory=lambda: Path(_get_env("AP_POLICY_DIR", "./data/policies")))
    report_dir: Path = field(default_factory=lambda: Path(_get_env("AP_REPORT_DIR", "./data/reports")))
    vectorstore_dir: Path = field(default_factory=lambda: Path(_get_env("AP_VECTORSTORE_DIR", "./data/vectorstore")))
    log_level: str = field(default_factory=lambda: _get_env("AP_LOG_LEVEL", "INFO"))

    def __post_init__(self) -> None:
        # Path 字段需要按相对路径解析
        for fld in ("life_table_dir", "policy_dir", "report_dir", "vectorstore_dir"):
            p = getattr(self, fld)
            if not p.is_absolute():
                object.__setattr__(self, fld, (ROOT_DIR / p).resolve())


# 全局单例（模块级缓存）
LLM_CONFIG = LLMConfig()
EMBEDDING_CONFIG = EmbeddingConfig()
APP_CONFIG = AppConfig()


def reload_config() -> None:
    """重新加载环境变量（供测试使用）。"""
    global LLM_CONFIG, EMBEDDING_CONFIG, APP_CONFIG  # noqa: PLW0603
    load_dotenv(ROOT_DIR / ".env", override=True)
    # pylint: disable=invalid-name
    LLM_CONFIG = LLMConfig()
    EMBEDDING_CONFIG = EmbeddingConfig()
    APP_CONFIG = AppConfig()