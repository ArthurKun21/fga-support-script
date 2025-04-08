from loguru import logger

from constants import (
    REPO_DIR_PATH,
)


async def check_if_repo_exists():
    """Check if the repository exists."""
    if not REPO_DIR_PATH.exists():
        logger.error(f"Support repository path does not exist: {REPO_DIR_PATH}")
        exit()

    logger.info(f"Support repository path exists: {REPO_DIR_PATH}")
