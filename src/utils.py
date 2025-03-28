from pathlib import Path

import orjson

from log import logger


def read_json(file_path: Path) -> list[dict]:
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = orjson.loads(f.read())

        return data
    except FileNotFoundError as e:
        logger.error(f"Error reading JSON file: {e}")
        return []
    except orjson.JSONDecodeError as e:
        logger.error(f"Error decoding JSON file: {e}")
        return []
    except Exception as e:
        logger.error(f"Error reading JSON file: {e}")
        return []


def write_json(file_path: Path, data):
    try:
        with open(file_path, "wb") as f:
            f.write(orjson.dumps(data, option=orjson.OPT_INDENT_2))
    except FileNotFoundError as e:
        logger.error(f"Error writing JSON file: {e}")
    except Exception as e:
        logger.error(f"Error writing JSON file: {e}")
