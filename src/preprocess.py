import os
from collections.abc import Callable, Coroutine
from pathlib import Path
from typing import Any

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
    if not CE_URL:
        logger.error("Craft essence URL is not set.")
        return []

    ce_data = await _process_data(
        name="ce",
        url=CE_URL,
        save_data_path=DATA_DIR / "craft_essence.json",
        preprocess_func=_preprocess_ce,
    )
    if not ce_data:
        logger.error("Failed to process craft essence data.")
        return []

    return ce_data


async def process_servant() -> list[ServantData]:
    if not SERVANT_URL:
        logger.error("Servant URL is not set.")
        return []

    servant_data = await _process_data(
        name="servant",
        url=SERVANT_URL,
        save_data_path=DATA_DIR / "servant.json",
        preprocess_func=_preprocess_servant,
    )
    if not servant_data:
        logger.error("Failed to process servant data.")
        return []

    return servant_data


async def _process_data[T](
    name: str,
    url: str,
    save_data_path: Path,
    preprocess_func: Callable[[list[dict]], Coroutine[Any, Any, list[T]]],
) -> list[T]:
    """
    Fetch and process data from a URL, and save it to a local file.

    Args:
        name (str): The name of the data.
        url (str): The URL to fetch the data from.
        save_data_path (Path): The path to save the processed data.
        preprocess_func (Callable): The function to preprocess the data.
    """
    logger.info(f"Processing {name} data...")

    if not url:
        logger.error(f"{name} URL is not set.")
        return []

    # Download data
    file_path = await utils.download_file(
        url=url,
        file_path=save_data_path,
    )
    if not file_path:
        logger.error(f"Failed to download {name} data.")
        return []

    # Read data
    raw_data: list[dict] | None = await utils.read_json(file_path)
    if raw_data is None:
        logger.error(f"Failed to read {name} data.")
        return []

    processed_data = await preprocess_func(raw_data)
    if not processed_data:
        logger.error(f"No {name} data found.")
        return []

    logger.info(f"{name} data processed successfully.")
    return processed_data


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
