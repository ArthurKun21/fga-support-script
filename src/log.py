import sys
from pathlib import Path
from loguru import logger

PROJECT_ROOT = Path(__file__).cwd()


def setup_logger():
    # Remove default logger
    logger.remove()

    # Set up logging
    logger.add(
        sink=PROJECT_ROOT / "logs" / "app.log",
        rotation="1 MB",
        level="DEBUG",
    )
    logger.add(
        sys.stderr,
        colorize=True,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> <level>{message}</level>",
        level="INFO",
    )


# Initialize logger when this module is imported
setup_logger()

# Export the logger
__all__ = ["logger"]
