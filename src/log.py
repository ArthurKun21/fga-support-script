import sys
from pathlib import Path

from loguru import logger

PROJECT_ROOT = Path(__file__).cwd()


def setup_logger():
    # Remove default logger
    logger.remove()

    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
        "<level>{message}</level>"
    )

    # Set up logging
    logger.add(
        sink=PROJECT_ROOT / "logs" / "app.log",
        rotation="1 MB",
        level="DEBUG",
        format=log_format,
    )
    logger.add(
        sys.stderr,
        colorize=True,
        format=log_format,
        level="INFO",
    )


# Initialize logger when this module is imported
setup_logger()

# Export the logger
__all__ = ["logger"]
