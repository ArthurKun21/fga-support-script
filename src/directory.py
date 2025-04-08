import os
from pathlib import Path

from loguru import logger

from constants import (
    REPO_CE_COLOR_DIR,
    REPO_CE_DIR,
    REPO_DIR_PATH,
    REPO_SERVANT_COLOR_DIR,
    REPO_SERVANT_DIR,
)
from enums import SupportKind
from models import SupportFolder


async def build_servant_index() -> None:
    logger.info("Building index...")

    # Build the index for each directory
    directories: set[tuple[Path, SupportKind]] = {
        (REPO_SERVANT_DIR, SupportKind.SERVANT),
        (REPO_SERVANT_COLOR_DIR, SupportKind.SERVANT),
        (REPO_CE_DIR, SupportKind.CRAFT_ESSENCE),
        (REPO_CE_COLOR_DIR, SupportKind.CRAFT_ESSENCE),
    }

    await _build_support_index(directories)


async def build_ce_index() -> None:
    logger.info("Building index...")

    # Build the index for each directory
    directories: set[tuple[Path, SupportKind]] = {
        (REPO_CE_DIR, SupportKind.CRAFT_ESSENCE),
        (REPO_CE_COLOR_DIR, SupportKind.CRAFT_ESSENCE),
    }

    await _build_support_index(directories)


async def _build_support_index(directories: set[tuple[Path, SupportKind]]):
    if not REPO_DIR_PATH.exists():
        logger.error(f"Support repository path does not exist: {REPO_DIR_PATH}")
        exit()

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

    try:
        for dirEntry in os.scandir(target_dir):
            dir_entry_path = Path(dirEntry.path)
            if not dir_entry_path.is_dir():
                logger.warning(f"Skipping non-directory entry: {dir_entry_path}")
                continue

            try:
                index = int(dir_entry_path.name)
            except ValueError:
                logger.warning(
                    f"Skipping invalid directory name: {dir_entry_path.name}"
                )
                continue

            txt_files = [
                file
                for file in dir_entry_path.iterdir()
                if file.is_file() and file.suffix == ".txt"
            ]
            if not txt_files:
                logger.warning(f"No .txt files found in directory: {dir_entry_path}")
                name = None
            else:
                txt_files = sorted(
                    txt_files,
                    key=lambda x: x.stat().st_mtime,
                    reverse=True,
                )

                name = txt_files[0].stem

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
