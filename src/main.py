import click
from anyio import run
from loguru import logger

import directory
from log import setup_logger


async def main(debug: bool):
    """
    Main function to run the application.
    """
    logger.info("Starting the application...")
    if debug:
        logger.debug("Debug mode is enabled.")
    await directory.build_index()


@click.command()
@click.option("--debug", is_flag=True, help="Enable debug mode.")
def app(debug: bool):
    setup_logger(debug=debug)

    run(main, debug)


if __name__ == "__main__":
    app()
