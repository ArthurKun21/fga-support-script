import asyncio
from pathlib import Path
from typing import Any

import httpx
import orjson
from anyio import open_file
from loguru import logger


async def read_json(file_path: Path) -> Any | None:
    try:
        async with await open_file(file_path, encoding="utf-8") as f:
            data = orjson.loads(await f.read())

        return data
    except FileNotFoundError as e:
        logger.error(f"Error reading JSON file: {e}")
        return None
    except orjson.JSONDecodeError as e:
        logger.error(f"Error decoding JSON file: {e}")
        return None
    except Exception as e:
        logger.error(f"Error reading JSON file: {e}")
        return None


async def write_json(file_path: Path, data):
    try:
        async with await open_file(file_path, "wb") as f:
            await f.write(orjson.dumps(data, option=orjson.OPT_INDENT_2))
    except FileNotFoundError as e:
        logger.error(f"Error writing JSON file: {e}")
    except Exception as e:
        logger.error(f"Error writing JSON file: {e}")


async def download_file(
    url: str,
    file_path: Path,
) -> Path | None:
    if file_path.exists() and file_path.stat().st_size > 100:
        logger.info(f"File already exists: {file_path}")
        return file_path

    retry = 3

    while retry > 0:
        try:
            async with (
                httpx.AsyncClient() as client,
                client.stream("GET", url) as response,
                await open_file(file_path, "wb") as f,
            ):
                async for chunk in response.aiter_bytes():
                    await f.write(chunk)
            return file_path
        except Exception as e:
            file_path.unlink(missing_ok=True)
            logger.error(f"Error downloading from Atlas {retry} retries left.\t{e}.")
            await asyncio.sleep(1)

            retry -= 1

    return None
