from pathlib import Path

from loguru import logger

PROJECT_ROOT = Path(__file__).cwd()

SUPPORT_PREVIEW_PATH = PROJECT_ROOT / "fga-support"


def build_index() -> None:
    logger.info("Building index...")
