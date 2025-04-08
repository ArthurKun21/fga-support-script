import click
from anyio import create_task_group, run
from loguru import logger

import directory
from data import process_craft_essence_data, process_servant_data
from log import setup_logger
from models import (
    CraftEssenceData,
    CraftEssenceDataIndexed,
    ServantData,
    ServantDataIndexed,
)
from preprocess import (
    fetch_local_ce_data,
    fetch_local_servant_data,
    process_craft_essence,
    process_servant,
)


async def main(debug: bool, dry_run: bool, delete: bool):
    """
    Main function to run the application.
    """
    logger.info("Starting the application...")
    if debug:
        logger.debug("Debug mode is enabled.")

    ce_latest_data: list[CraftEssenceData] = []
    ce_local_data: CraftEssenceDataIndexed = {}

    servant_latest_data: list[ServantData] = []
    servant_local_data: ServantDataIndexed = {}

    async def preprocess_ce():
        nonlocal ce_latest_data
        ce_latest_data = await process_craft_essence()

    async def fetch_local_ce():
        nonlocal ce_local_data
        ce_local_data = await fetch_local_ce_data()

    async def preprocess_servant():
        nonlocal servant_latest_data
        servant_latest_data = await process_servant()

    async def fetch_local_servant():
        nonlocal servant_local_data
        servant_local_data = await fetch_local_servant_data()

    await directory.check_if_repo_exists()

    if delete:
        logger.info("Deleting the repository support files...")
        await directory.delete_repository_support()

    try:
        async with create_task_group() as tg:
            tg.start_soon(preprocess_ce)
            tg.start_soon(fetch_local_ce)
            tg.start_soon(preprocess_servant)
            tg.start_soon(fetch_local_servant)
    except Exception as e:
        logger.error(f"An error occurred: {e}")

    try:
        async with create_task_group() as tg:
            tg.start_soon(
                process_servant_data,
                servant_latest_data,
                servant_local_data,
                debug,
                dry_run,
            )
            tg.start_soon(
                process_craft_essence_data,
                ce_latest_data,
                ce_local_data,
                debug,
                dry_run,
            )
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        exit()

    await directory.copy_output_to_repo()

    await directory.remove_duplicate_txt_names()


@click.command()
@click.option("--debug", is_flag=True, help="Enable debug mode.")
@click.option("--dry_run", is_flag=True, help="Enable dry run mode.")
@click.option("--delete", is_flag=True, help="Delete the repository files.")
def app(debug: bool, dry_run: bool, delete: bool):
    setup_logger(debug=debug)

    run(main, debug, dry_run, delete)


if __name__ == "__main__":
    app()
