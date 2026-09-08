from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path


def setup_logging(
    log_directory: str = "logs",
) -> logging.Logger:
    """Configure application logging."""

    log_path = Path(log_directory)
    log_path.mkdir(
        parents=True,
        exist_ok=True,
    )

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    log_file = (
        log_path
        / f"azure_resource_audit_{timestamp}.log"
    )

    logger = logging.getLogger(
        "azure_resource_audit"
    )

    logger.setLevel(logging.INFO)

    # Prevent duplicate handlers if setup_logging()
    # is called more than once.
    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        "%(asctime)s | "
        "%(levelname)s | "
        "%(name)s | "
        "%(message)s"
    )

    file_handler = logging.FileHandler(
        log_file,
        encoding="utf-8",
    )

    file_handler.setFormatter(
        formatter
    )

    console_handler = logging.StreamHandler()

    console_handler.setFormatter(
        formatter
    )

    logger.addHandler(
        file_handler
    )

    logger.addHandler(
        console_handler
    )

    logger.propagate = False

    return logger