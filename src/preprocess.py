import os
from pathlib import Path

from loguru import logger

import utils
from models import Assets, CraftEssenceData, ServantData

PROJECT_ROOT = Path(__file__).cwd()

DATA_DIR = PROJECT_ROOT / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

SERVANT_URL: str | None = os.getenv("SERVANT_URL", None)
CE_URL: str | None = os.getenv("CE_URL", None)

LOCAL_CE_DATA = DATA_DIR / "local_ce.json"
LOCAL_SERVANT_DATA = DATA_DIR / "local_servant.json"

type CraftEssenceDataIndexed = dict[int, CraftEssenceData]
type ServantDataIndexed = dict[int, ServantData]


async def fetch_local_ce_data() -> CraftEssenceDataIndexed:
    return await _fetch_local_data(
        name="craft essence",
        local_data_path=LOCAL_CE_DATA,
        class_type=CraftEssenceData,
    )


async def fetch_local_servant_data() -> ServantDataIndexed:
    return await _fetch_local_data(
        name="servant",
        local_data_path=LOCAL_SERVANT_DATA,
        class_type=ServantData,
    )


async def _fetch_local_data[T](
    name: str,
    local_data_path: Path,
    class_type: type[T],
) -> dict[int, T]:
    """
    Fetch local data from a JSON file. And then convert it to a dictionary
    with the index as the key and the class as the value.

    Args:
        name (str): The name of the data.
        local_data_path (Path): The path to the local data file.
        class_type (type[T]): The class type to convert the data to.
    """
    logger.info(f"Fetching local {name} data...")

    if not local_data_path.exists():
        logger.warning(f"Local {name} data file does not exist.")
        return {}

    # Read local craft essence data
    raw_data: list[dict] | None = await utils.read_json(local_data_path)
    if raw_data is None:
        logger.error(f"Failed to read local {name} data.")
        return {}

    try:
        data = {item["idx"]: class_type(**item) for item in raw_data}

        return data
    except KeyError as e:
        logger.error(f"Key error while processing local {name} data: {e}")
        return {}
    except TypeError as e:
        logger.error(f"Type error while processing local {name} data: {e}")
        return {}
    except Exception as e:
        logger.error(f"Unexpected error while processing local {name} data: {e}")
        return {}


async def process_craft_essence() -> list[CraftEssenceData]:
    logger.info("Processing craft essence data...")

    if not CE_URL:
        logger.error("Craft essence URL is not set.")
        return []

    # Download craft essence data
    craft_essence_file_path = await utils.download_file(
        url=CE_URL,
        file_path=DATA_DIR / "craft_essence.json",
    )
    if not craft_essence_file_path:
        logger.error("Failed to download craft essence data.")
        return []

    # Read craft essence data
    raw_data: list[dict] | None = await utils.read_json(craft_essence_file_path)
    if raw_data is None:
        logger.error("Failed to read craft essence data.")
        return []

    ce_data = await _preprocess_ce(raw_data)
    if not ce_data:
        logger.error("No craft essence data found.")
        return []

    logger.info("Craft essence data processed successfully.")
    return ce_data


async def process_servant():
    logger.info("Processing servant data...")

    if not SERVANT_URL:
        logger.error("Servant URL is not set.")
        return

    # Download servant data
    servant_file_path = await utils.download_file(
        url=SERVANT_URL,
        file_path=DATA_DIR / "servant.json",
    )
    if not servant_file_path:
        logger.error("Failed to download servant data.")
        return

    # Read servant data
    raw_data: list[dict] | None = await utils.read_json(servant_file_path)
    if raw_data is None:
        logger.error("Failed to read servant data.")
        return

    servant_data = await _preprocess_servant(raw_data)
    if not servant_data:
        logger.error("No servant data found.")
        return

    logger.info("Servant data processed successfully.")
    return servant_data


async def _preprocess_ce(raw_data: list[dict]) -> list[CraftEssenceData]:
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

    return ce_data_list


async def _preprocess_servant(raw_data: list[dict]) -> list[ServantData]:
    sorted_data = sorted(raw_data, key=lambda x: x["collectionNo"])

    servant_data_list: list[ServantData] = []

    for data in sorted_data:
        collectionNo = data.get("collectionNo", 0)
        if collectionNo == 0:
            continue

        name = data.get("name", "")
        class_name = data.get("className", "")
        rarity = data.get("rarity", 1)

        extra_assets = data.get("extraAssets", {})

        face_data = extra_assets.get("face", {})
        face_list = []

        for value in face_data.values():
            if value:
                face_list.append(value)

        new_data = ServantData(
            idx=collectionNo,
            name=name,
            class_name=class_name,
            faces=[Assets(url=face) for face in face_list],
            rarity=rarity,
        )

        servant_data_list.append(new_data)

    return servant_data_list
