from pathlib import Path

import constants
from log import logger
import utils

PROJECT_ROOT = Path(__file__).cwd()

DATA_DIR = PROJECT_ROOT / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)


def process_craft_essence():
    logger.info("Processing craft essence data...")

    # Download craft essence data
    craft_essence_file_path = utils.download_file(
        url=constants.CRAFT_ESSENCE_DATA_URL,
        file_path=DATA_DIR / "craft_essence.json",
    )
    if not craft_essence_file_path:
        logger.error("Failed to download craft essence data.")
        return

    # Read craft essence data
    # craft_essence_data = utils.read_json(craft_essence_file_path)


def process_servant():
    logger.info("Processing servant data...")

    # Download servant data
    servant_file_path = utils.download_file(
        url=constants.SERVANT_DATA_URL,
        file_path=DATA_DIR / "servant.json",
    )
    if not servant_file_path:
        logger.error("Failed to download servant data.")
        return

    # Read servant data
    # servant_data = utils.read_json(servant_file_path)
