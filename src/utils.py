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
    debug: bool = False,
) -> Path | None:
    if file_path.exists() and file_path.stat().st_size > 100:
        logger.debug(f"File already exists: {file_path}")
        return file_path

    logger.info(f"Downloading file from url to {file_path}...")

    if debug:
        logger.debug(
            "Debug mode enabled. Skipping download and "
            f"Creating empty file {file_path.name}."
        )
        async with await open_file(file_path, "wb") as f:
            pass
        return file_path

    retry = 3

    while retry > 0:
        try:
            async_file = await open_file(file_path, "wb")
            async with (
                httpx.AsyncClient() as client,
                client.stream("GET", url) as response,
                async_file as f,
            ):
                async for chunk in response.aiter_bytes():
                    await f.write(chunk)
            return file_path
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error occurred: {e}")
            file_path.unlink(missing_ok=True)
        except httpx.ConnectError as e:
            logger.error(f"Connection error occurred: {e}")
            file_path.unlink(missing_ok=True)
        except httpx.TimeoutException as e:
            logger.error(f"Timeout error occurred: {e}")
            file_path.unlink(missing_ok=True)
        except httpx.NetworkError as e:
            logger.error(f"Network error occurred: {e}")
            file_path.unlink(missing_ok=True)
        except Exception as e:
            logger.error(f"An error occurred: {e}")
            file_path.unlink(missing_ok=True)

        logger.error(f"Error downloading from Atlas {retry} retries left.")
        await asyncio.sleep(1)

        retry -= 1

    return None
