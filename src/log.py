import sys

from loguru import logger

from constants import LOG_FILE


def setup_logger(debug: bool = False):
    # Remove default logger
    logger.remove()

    debug_log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
        "<level>{message}</level>"
    )

    # Set up logging
    logger.add(
        sink=LOG_FILE,
        rotation="1 MB",
        level="DEBUG",
        format=debug_log_format,
    )

    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<level>{message}</level>"
    )
    level = "DEBUG" if debug else "INFO"
    current_format = debug_log_format if debug else log_format

    logger.add(
        sys.stderr,
        colorize=True,
        format=current_format,
        level=level,
    )
