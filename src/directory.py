from pathlib import Path
from typing import Tuple
from log import logger
from models import SupportFolder

PROJECT_ROOT = Path(__file__).cwd()

SUPPORT_PREVIEW_PATH = PROJECT_ROOT / "fga-support"

SUPPORT_OLD_PATH = PROJECT_ROOT / "fga-old-support"


def read_craft_essence(directory: Path) -> list[SupportFolder]:
    craft_essence_path = directory / "craft_essence"
    if not craft_essence_path.exists():
        logger.error(f"Craft Essence path does not exist: {craft_essence_path}")
        return []

    craft_essence_support_list: list[SupportFolder] = []

    for folder in craft_essence_path.iterdir():
        if folder.is_dir():
            txt_file = list(folder.glob("*.txt"))
            if not txt_file:
                logger.warning(f"Missing .txt file in Craft Essence folder: {folder}")
                continue

            name = txt_file[0].stem

            support_folder = SupportFolder(path=folder, name=name, idx=int(folder.name))
            craft_essence_support_list.append(support_folder)

    return craft_essence_support_list


def read_servant(directory: Path) -> list[SupportFolder]:
    servant_path = directory / "servant"
    if not servant_path.exists():
        logger.error(f"Servant path does not exist: {servant_path}")
        return []

    servant_support_list: list[SupportFolder] = []

    for folder in servant_path.iterdir():
        if folder.is_dir():
            txt_file = list(folder.glob("*.txt"))
            if not txt_file:
                logger.warning(f"Missing .txt file in Servant folder: {folder}")
                continue

            name = txt_file[0].stem

            support_folder = SupportFolder(path=folder, name=name, idx=int(folder.name))
            servant_support_list.append(support_folder)

    return servant_support_list


def read_support_preview() -> Tuple[list[SupportFolder], list[SupportFolder]]:
    if not SUPPORT_PREVIEW_PATH.exists():
        logger.error(f"Support preview path does not exist: {SUPPORT_PREVIEW_PATH}")
        return [], []

    servant_list = read_servant(SUPPORT_PREVIEW_PATH)
    craft_essence_list = read_craft_essence(SUPPORT_PREVIEW_PATH)

    return servant_list, craft_essence_list


def read_support_old() -> Tuple[list[SupportFolder], list[SupportFolder]]:
    if not SUPPORT_OLD_PATH.exists():
        logger.error(f"Old support path does not exist: {SUPPORT_OLD_PATH}")
        return [], []

    servant_list = read_servant(SUPPORT_OLD_PATH)
    craft_essence_list = read_craft_essence(SUPPORT_OLD_PATH)

    return servant_list, craft_essence_list
