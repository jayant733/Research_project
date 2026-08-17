"""
Dependency injection-based logging wrappers for the training engine.
Replaces print statements with standardized Python logging.
"""

import logging
import sys


def get_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """
    Constructs a standardized logger for a component.
    Supports future telemetry subscription.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if not logger.handlers:
        # Console logger
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger
