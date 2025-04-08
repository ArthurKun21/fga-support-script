import os
from pathlib import Path

from anyio import create_task_group
from loguru import logger

from constants import (
    REPO_CE_COLOR_DIR,
    REPO_CE_DIR,
    REPO_DIR_PATH,
    REPO_SERVANT_COLOR_DIR,
    REPO_SERVANT_DIR,
)


async def check_if_repo_exists():
    """Check if the repository exists."""
    if not REPO_DIR_PATH.exists():
        logger.error(f"Support repository path does not exist: {REPO_DIR_PATH}")
        exit()

    logger.info(f"Support repository path exists: {REPO_DIR_PATH}")


async def remove_duplicate_txt_names():
    """Remove duplicate text names."""

    directories = [
        REPO_SERVANT_DIR,
        REPO_SERVANT_COLOR_DIR,
        REPO_CE_DIR,
        REPO_CE_COLOR_DIR,
    ]

    async with create_task_group() as tg:
        for directory in directories:
            tg.start_soon(_remove_duplicate_txt_names, directory)


async def _remove_duplicate_txt_names(directory: Path):
    """Remove duplicate text names in a directory."""
    if not directory.exists():
        logger.error(f"Directory does not exist: {directory}")
        return

    try:
        for dirEntry in os.scandir(directory):
            if dirEntry.is_file():
                continue

            dir_path = Path(dirEntry.path)

            # Remove the old txt files
            txt_files = [f for f in dir_path.glob("*.txt")]
            txt_files.sort(key=lambda x: x.stat().st_mtime)

            if not txt_files:
                logger.warning(f"No txt files found in {dir_path}")
                continue

            for i in txt_files[1:]:
                try:
                    i.unlink(missing_ok=True)
                    logger.info(f"Removed duplicate file: {i}")
                except FileNotFoundError:
                    logger.error(f"File not found when trying to remove: {i}")
                except PermissionError:
                    logger.error(f"Permission denied when trying to remove: {i}")
                except Exception as e:
                    logger.error(f"Error removing file {i}: {e}")
    except OSError as e:
        logger.error(f"OS error occurred: {e}")
    except Exception as e:
        logger.error(f"An error occurred: {e}")
