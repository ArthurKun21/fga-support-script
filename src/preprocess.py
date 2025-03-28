from pathlib import Path
from log import logger

CWD = Path(__file__).cwd()


def process():
    logger.info("Starting the preprocessing...")
