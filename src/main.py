import click
from anyio import create_task_group, run
from loguru import logger

import directory
from log import setup_logger
from models import CraftEssenceData
from preprocess import process_craft_essence


async def main(debug: bool):
    """
    Main function to run the application.
    """
    logger.info("Starting the application...")
    if debug:
        logger.debug("Debug mode is enabled.")

    ce_latest_data: list[CraftEssenceData] = []

    async def preprocess_ce():
        nonlocal ce_latest_data
        ce_latest_data = await process_craft_essence()

    async with create_task_group() as tg:
        tg.start_soon(directory.build_index)
        tg.start_soon(preprocess_ce)


@click.command()
@click.option("--debug", is_flag=True, help="Enable debug mode.")
def app(debug: bool):
    setup_logger(debug=debug)

    run(main, debug)


if __name__ == "__main__":
    app()
