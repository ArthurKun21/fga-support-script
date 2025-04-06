import sys
from pathlib import Path

from loguru import logger

PROJECT_ROOT = Path(__file__).cwd()


def setup_logger(debug: bool = False):
    # Remove default logger
    logger.remove()

    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
        "<level>{message}</level>"
    )

    logs_dir = PROJECT_ROOT / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)

    # Set up logging
    logger.add(
        sink=logs_dir / "app.log",
        rotation="1 MB",
        level="DEBUG",
        format=log_format,
    )

    level = "DEBUG" if debug else "INFO"

    logger.add(
        sys.stderr,
        colorize=True,
        format=log_format,
        level=level,
    )
