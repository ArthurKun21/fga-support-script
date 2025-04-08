import os
import shutil
from pathlib import Path

from anyio import create_task_group
from loguru import logger

from constants import (
    OUTPUT_DIR,
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


async def copy_output_to_repo():
    """Copy output files to the repository."""
    logger.info("Copying images to the repository...")
    try:
        shutil.copytree(
            OUTPUT_DIR,
            REPO_DIR_PATH,
            dirs_exist_ok=True,
        )
        logger.info("Successfully copied output files to the repository.")
    except FileExistsError:
        logger.error("The repository already has the output files.")
    except FileNotFoundError:
        logger.error("The output directory was not found.")
    except Exception as e:
        logger.error(f"Error copying output files to the repository: {e}")


async def delete_repository_support():
    """Delete the repository support to reset."""
    if not REPO_DIR_PATH.exists():
        logger.error(f"Support repository path does not exist: {REPO_DIR_PATH}")
        return

    directories = [
        REPO_SERVANT_DIR,
        REPO_SERVANT_COLOR_DIR,
        REPO_CE_DIR,
        REPO_CE_COLOR_DIR,
    ]

    for dirEntry in directories:
        if not dirEntry.exists():
            logger.warning(f"Directory does not exist: {dirEntry}")
            continue

        for item in dirEntry.iterdir():
            if item.is_file():
                item.unlink(missing_ok=True)
            elif item.is_dir():
                try:
                    shutil.rmtree(item, ignore_errors=True)
                except Exception:
                    continue

        logger.info(f"Removed files and directories in directory: {dirEntry.name}")


async def remove_duplicate_txt_names():
    """Remove duplicate text names."""

    logger.info("Removing duplicate text names...")
    directories = [
        REPO_SERVANT_DIR,
        REPO_SERVANT_COLOR_DIR,
        REPO_CE_DIR,
        REPO_CE_COLOR_DIR,
    ]
    try:
        async with create_task_group() as tg:
            for directory in directories:
                tg.start_soon(_remove_duplicate_txt_names, directory)
    except Exception as e:
        logger.error(f"Error removing duplicate text names: {e}")


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
            txt_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)

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
