import click
from anyio import run
from loguru import logger

import directory
from log import setup_logger


async def main():
    """
    Main function to run the application.
    """
    logger.info("Starting the application...")
    await directory.build_index()


@click.command()
@click.option("--debug", is_flag=True, help="Enable debug mode.")
def app(debug: bool):
    setup_logger(debug=debug)
    if debug:
        logger.debug("Debug mode is enabled.")

    run(main)


if __name__ == "__main__":
    app()
