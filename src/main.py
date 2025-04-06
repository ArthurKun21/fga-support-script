import click
from anyio import create_task_group, run
from loguru import logger

import directory
from log import setup_logger
from models import CraftEssenceData
from preprocess import (
    CraftEssenceDataIndexed,
    fetch_local_ce_data,
    process_craft_essence,
)


async def main(debug: bool):
    """
    Main function to run the application.
    """
    logger.info("Starting the application...")
    if debug:
        logger.debug("Debug mode is enabled.")

    ce_latest_data: list[CraftEssenceData] = []
    ce_local_data: CraftEssenceDataIndexed = {}

    async def preprocess_ce():
        nonlocal ce_latest_data
        ce_latest_data = await process_craft_essence()

    async def fetch_local_ce():
        nonlocal ce_local_data
        ce_local_data = await fetch_local_ce_data()

    async with create_task_group() as tg:
        tg.start_soon(directory.build_index)
        tg.start_soon(preprocess_ce)
        tg.start_soon(fetch_local_ce)


@click.command()
@click.option("--debug", is_flag=True, help="Enable debug mode.")
def app(debug: bool):
    setup_logger(debug=debug)

    run(main, debug)


if __name__ == "__main__":
    app()
