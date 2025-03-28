from pathlib import Path
from loguru import logger
import sys

CWD = Path(__file__).cwd()

# Set up logging
logger.remove()
logger.add(
    CWD / "logs" / "app.log", rotation="1 MB", retention="10 days", level="DEBUG"
)
logger.add(sys.stderr, level="INFO")


def main():
    """
    Main function to run the application.
    """
    logger.info("Starting the application...")
    # Your application logic goes here
    logger.info("Application finished successfully.")


if __name__ == "__main__":
    main()
