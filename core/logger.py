"""
Centralized logging configuration for the CSV Analytics System.

Demonstrates:
- Standard library `logging` module hierarchy
- Handler attachment, formatting, and level management
- Consistent formatting across CLI, Streamlit, and tests
"""

import logging
import sys
from typing import Optional

_CONFIGURED = False


def setup_logging(
    level: int = logging.INFO,
    format_str: Optional[str] = None,
) -> logging.Logger:
    """
    Configures and returns the root logger for the csv_agent application namespace.
    """
    global _CONFIGURED

    app_logger = logging.getLogger("csv_agent")

    if not _CONFIGURED:
        app_logger.setLevel(level)
        app_logger.propagate = False

        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(level)

        default_fmt = "%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d - %(message)s"
        formatter = logging.Formatter(format_str or default_fmt, datefmt="%H:%M:%S")
        handler.setFormatter(formatter)

        app_logger.addHandler(handler)
        _CONFIGURED = True

    return app_logger


def get_logger(module_name: str) -> logging.Logger:
    """Convenience helper to retrieve namespaced loggers."""
    if not _CONFIGURED:
        setup_logging()
    return logging.getLogger(f"csv_agent.{module_name}")
