from log import logger
import preprocess


def main():
    """
    Main function to run the application.
    """
    logger.info("Starting the application...")
    # Your application logic goes here
    logger.info("Application finished successfully.")

    preprocess.process()


if __name__ == "__main__":
    main()
