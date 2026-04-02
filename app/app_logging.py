from __future__ import annotations

import logging
from pathlib import Path


LOGGER_NAME = "housekeeping_desktop"


def log_path() -> Path:
    return Path(__file__).resolve().parent.parent / "logs" / "inspection.log"


def configure_logging() -> logging.Logger:
    logger = logging.getLogger(LOGGER_NAME)
    if logger.handlers:
        return logger

    target = log_path()
    target.parent.mkdir(parents=True, exist_ok=True)

    handler = logging.FileHandler(target, encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))

    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    logger.propagate = False
    logger.info("Logging initialized at %s", target)
    return logger


def get_logger() -> logging.Logger:
    return logging.getLogger(LOGGER_NAME)
