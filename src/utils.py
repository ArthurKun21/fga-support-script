import time
from pathlib import Path
from typing import Optional

import httpx
import orjson

from log import logger


def read_json(file_path: Path):
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


def download_file(
    url: str,
    file_path: Path,
) -> Optional[Path]:
    if file_path.exists() and file_path.stat().st_size > 100:
        logger.info(f"File already exists: {file_path}")
        return file_path

    retry = 3

    while retry > 0:
        try:
            with httpx.stream("GET", url) as response:
                with open(file_path, "wb") as f:
                    for chunk in response.iter_bytes():
                        f.write(chunk)
            return file_path
        except Exception as e:
            file_path.unlink(missing_ok=True)
            logger.error(f"Error downloading from Atlas {retry} retries left.\t{e}.")
            time.sleep(1)

            retry -= 1

    return None
