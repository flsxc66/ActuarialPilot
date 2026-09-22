"""统一的日志记录器。"""

from __future__ import annotations

import logging
import sys

from ..config import APP_CONFIG


def get_logger(name: str) -> logging.Logger:
    """返回一个绑定到 ActuarialPilot 根 logger 的子 logger。
    多次调用同名 logger 不会重复添加 handler。
    """
    logger = logging.getLogger(f"actuarial_pilot.{name}")

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stderr)
        formatter = logging.Formatter(
            "[%(asctime)s] %(levelname)s [%(name)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    logger.setLevel(APP_CONFIG.log_level.upper())
    logger.propagate = False
    return logger