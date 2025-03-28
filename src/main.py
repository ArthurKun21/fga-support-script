import sys
from pathlib import Path

from loguru import logger

CWD = Path(__file__).cwd()

# Set up logging
logger.add(
    sink=CWD / "logs" / "app.log",
    rotation="1 MB",
    level="DEBUG",
)
logger.add(
    sys.stderr,
    colorize=True,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> <level>{message}</level>",
    level="INFO",
)


def main():
    """
    Main function to run the application.
    """
    logger.info("Starting the application...")
    # Your application logic goes here
    logger.info("Application finished successfully.")


if __name__ == "__main__":
    main()
