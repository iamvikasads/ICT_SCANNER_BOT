"""
Single shared logger used across the whole bot.
Rotating file handler + console handler.
"""
import logging
from logging.handlers import RotatingFileHandler

from config import settings


def get_logger(name: str = "ema_bot") -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        # Already configured (avoid duplicate handlers on repeated imports)
        return logger

    logger.setLevel(logging.INFO)

    fmt = logging.Formatter(
        "%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler = RotatingFileHandler(
        settings.LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=5
    )
    file_handler.setFormatter(fmt)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(fmt)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger
