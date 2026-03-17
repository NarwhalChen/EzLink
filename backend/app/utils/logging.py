"""Structured logging setup using the standard library."""

import logging
import sys


def configure_logging(level: int = logging.INFO) -> None:
    """Configure root logger with a structured, timestamped format."""
    fmt = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    logging.basicConfig(
        level=level,
        format=fmt,
        datefmt="%Y-%m-%dT%H:%M:%S",
        stream=sys.stdout,
        force=True,
    )


def get_logger(name: str) -> logging.Logger:
    """Return a named logger.  Call configure_logging() once at app startup."""
    return logging.getLogger(name)
