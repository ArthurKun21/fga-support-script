from anyio import run

from log import setup_logger

logger = setup_logger()


async def main():
    """
    Main function to run the application.
    """
    logger.info("Starting the application...")
    # Your application logic goes here
    logger.info("Application finished successfully.")


if __name__ == "__main__":
    run(main)
