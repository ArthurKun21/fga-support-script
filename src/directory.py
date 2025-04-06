import os
import re
from pathlib import Path

from loguru import logger

from enums import SupportKind
from models import SupportFolder

PROJECT_ROOT = Path(__file__).cwd()

SUPPORT_PREVIEW_PATH = PROJECT_ROOT / "fga-support"


async def build_index() -> None:
    logger.info("Building index...")

    if not SUPPORT_PREVIEW_PATH.exists():
        logger.error(f"Support preview path does not exist: {SUPPORT_PREVIEW_PATH}")
        exit()

    await build_servant_index()


async def build_servant_index() -> list[SupportFolder]:
    servant_dir = SUPPORT_PREVIEW_PATH / "servant"

    if not servant_dir.exists():
        servant_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Empty Servant directory created at {servant_dir}")
        return []

    logger.info(f"Building servant index at {servant_dir}...")

    entries: list[SupportFolder] = []

    index_regex = re.compile(r"^\d+_[\w]+$")

    try:
        for dirEntry in os.scandir(servant_dir):
            dir_entry_path = Path(dirEntry.path)
            if not dir_entry_path.is_dir():
                logger.warning(f"Skipping non-directory entry: {dir_entry_path}")
                continue

            name = dir_entry_path.name
            match = index_regex.match(name)

            if match:
                digits = int(match.group(0))
                support_folder = SupportFolder(
                    path=dir_entry_path,
                    name=name,
                    idx=digits,
                    kind=SupportKind.SERVANT,
                )
                logger.debug(f"Found valid servant directory: {support_folder}")
                entries.append(support_folder)

    except OSError as e:
        logger.error(f"Error accessing directory {servant_dir}: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    if not entries:
        logger.debug("No valid servant directories found.")
    return entries
