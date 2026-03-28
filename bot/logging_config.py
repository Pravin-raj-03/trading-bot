"""Logging configuration for the trading bot.

This module sets up structured logging for the application, creating both
console and file handlers with appropriate severity levels and formatting.
"""

import logging
import os
import sys
from datetime import datetime
from typing import Optional


def setup_logging(
    log_level: int = logging.INFO,
    log_dir: str = "logs",
) -> logging.Logger:
    """Configures global logging for the application.

    Creates a logger with both a console handler (INFO level) and a
    timestamped file handler (DEBUG level) for persistent storage.

    Args:
        log_level: The primary log level for the root logger.
        log_dir: The directory where log files will be stored.

    Returns:
        The configured logger instance.
    """
    logger = logging.getLogger("trading_bot")
    
    # Avoid duplicate handlers if already configured
    if logger.hasHandlers():
        return logger

    logger.setLevel(logging.DEBUG)

    # Logging format string
    log_format = "%(asctime)s | %(levelname)-7s | %(name)s | %(message)s"
    formatter = logging.Formatter(log_format, datefmt="%H:%M:%S")

    # Console Handler (INFO)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File Handler (DEBUG)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"trading_bot_{timestamp}.log")
    
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger
