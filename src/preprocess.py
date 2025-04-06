from pathlib import Path

import constants
import utils
from log import logger
from models import Assets, CraftEssenceData

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
    raw_data: list[dict] = utils.read_json(craft_essence_file_path)

    _preprocess_ce(raw_data)


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
    # raw_data:list[dict] = utils.read_json(servant_file_path)


def _preprocess_ce(
    raw_data: list[dict],  # type: ignore[valid-type,assignment]  # noqa: F821
):
    sorted_data = sorted(raw_data, key=lambda x: x["collectionNo"])

    ce_data_list: list[CraftEssenceData] = []

    for ce in sorted_data:
        collectionNo = ce.get("collectionNo", 0)
        if collectionNo == 0:
            continue

        name = ce.get("name", "")

        rarity = ce.get("rarity", 1)

        extra_assets = ce.get("extraAssets", {})

        equip_face = extra_assets.get("equipFace", {})

        equip = equip_face.get("equip", {})

        for value in equip.values():
            if value:
                face = value
                break
        else:
            face = ""

        new_data = CraftEssenceData(
            idx=collectionNo,
            name=name,
            faces=Assets(url=face) if face else None,
            rarity=rarity,
        )

        ce_data_list.append(new_data)
