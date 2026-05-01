"""
Logging configuration for the trading bot.

Sets up dual handlers:
  - Console  : INFO-level, colorized via rich
  - File     : DEBUG-level, rotating (5 MB × 3 backups)
"""

import logging
import os
from logging.handlers import RotatingFileHandler

from rich.logging import RichHandler

LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
LOG_FILE = os.path.join(LOG_DIR, "trading_bot.log")
LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_logging() -> logging.Logger:
    """Configure and return the root application logger."""
    os.makedirs(LOG_DIR, exist_ok=True)

    logger = logging.getLogger("trading_bot")
    logger.setLevel(logging.DEBUG)

    # Prevent duplicate handlers on repeated calls
    if logger.handlers:
        return logger

    # ── Console handler (INFO) via Rich ──────────────────────────────
    console_handler = RichHandler(
        level=logging.INFO,
        rich_tracebacks=True,
        show_time=False,
        show_path=False,
    )
    console_handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(console_handler)

    # ── File handler (DEBUG) with rotation ───────────────────────────
    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=5 * 1024 * 1024,  # 5 MB
        backupCount=3,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT))
    logger.addHandler(file_handler)

    logger.debug("Logging initialised – file: %s", LOG_FILE)
    return logger
