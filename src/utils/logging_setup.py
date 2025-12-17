"""Logging configuration for the research assistant."""

import logging
import sys
from pathlib import Path
from typing import Optional


def setup_logging(
    log_file: str = "logs/research.log",
    level: str = "INFO",
    console: bool = True
) -> logging.Logger:
    """
    Configure logging with file and console handlers.

    Args:
        log_file: Path to log file
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
        console: Whether to log to console

    Returns:
        Configured logger instance
    """
    # Create logs directory if needed
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    # Get root logger
    logger = logging.getLogger("research_assistant")
    logger.setLevel(getattr(logging, level.upper()))

    # Clear any existing handlers
    logger.handlers.clear()

    # Format for log messages
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # File handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)  # Log everything to file
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Console handler (if enabled)
    if console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, level.upper()))
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Get a logger instance.

    Args:
        name: Logger name (typically __name__ of calling module)

    Returns:
        Logger instance
    """
    if name:
        return logging.getLogger(f"research_assistant.{name}")
    return logging.getLogger("research_assistant")
