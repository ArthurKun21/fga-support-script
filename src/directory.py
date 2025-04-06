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

    servant_dir = SUPPORT_PREVIEW_PATH / "servant"
    servant_color_dir = SUPPORT_PREVIEW_PATH / "servant-color"

    ce_dir = SUPPORT_PREVIEW_PATH / "ce"
    ce_color_dir = SUPPORT_PREVIEW_PATH / "ce-color"

    # Build the index for each directory
    directories: set[tuple[Path, SupportKind]] = {
        (servant_dir, SupportKind.SERVANT),
        (servant_color_dir, SupportKind.SERVANT),
        (ce_dir, SupportKind.CRAFT_ESSENCE),
        (ce_color_dir, SupportKind.CRAFT_ESSENCE),
    }

    for target_dir, kind in directories:
        await _build_index(target_dir, kind)


async def _build_index(
    target_dir: Path,
    kind: SupportKind,
) -> list[SupportFolder]:
    """Build the index from the given directory."""

    if not target_dir.exists():
        target_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Empty {kind} directory created at {target_dir}")
        return []

    logger.info(f"Building {kind} index at {target_dir}...")

    entries: list[SupportFolder] = []

    index_regex = re.compile(r"^(\d+)_([\w\-\s]+)$")

    try:
        for dirEntry in os.scandir(target_dir):
            dir_entry_path = Path(dirEntry.path)
            if not dir_entry_path.is_dir():
                logger.warning(f"Skipping non-directory entry: {dir_entry_path}")
                continue

            dir_name = dir_entry_path.name
            match = index_regex.match(str(dir_name))

            if not match:
                logger.debug(f"Invalid directory name format: {dir_name}")
                continue

            index = int(match.group(1))
            name = match.group(2)
            support_folder = SupportFolder(
                path=dir_entry_path,
                name=name,
                idx=index,
                kind=kind,
            )
            logger.debug(f"Found valid {kind} directory: {support_folder}")
            entries.append(support_folder)

    except OSError as e:
        logger.error(f"Error accessing directory {target_dir}: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    if not entries:
        logger.debug(f"No valid {kind} directories found.")
    return entries
