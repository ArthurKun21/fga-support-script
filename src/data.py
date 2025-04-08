import asyncio
from concurrent.futures import as_completed
from pathlib import Path

import cv2
from anyio import to_thread
from anyio.from_thread import start_blocking_portal
from loguru import logger

import image
from constants import (
    LOCAL_SERVANT_DATA,
    OUTPUT_SERVANT_COLOR_DIR,
    OUTPUT_SERVANT_DIR,
    TEMP_SERVANT_DIR,
)
from models import (
    Assets,
    CraftEssenceData,
    CraftEssenceDataIndexed,
    ServantData,
    ServantDataIndexed,
)
from utils import download_file, write_json

ROOT = Path(__file__).cwd()


async def _download_and_confirm_asset(
    download_dir: Path, asset: Assets
) -> Assets | None:
    """Download and confirm the asset.
    Args:
        download_dir (Path): The directory to download the asset to.
        asset (Assets): The asset to download.
    Returns:
        Assets | None: The asset if successful, None otherwise.
    """
    file_path = await download_file(
        asset.url,
        download_dir / f"{asset.key}-{asset.url_file_name}",
    )
    if file_path is None:
        logger.error(f"Failed to download asset: {asset.key}")
        return None

    try:
        img = cv2.imread(str(file_path))
        if img is None:
            logger.error(f"Failed to read image: {file_path}")
            return None

        # Check if the image is empty
        if img.size == 0:
            logger.error(f"Empty image: {file_path}")
            return None

        return asset
    except Exception as e:
        logger.error(f"Error reading image: {file_path} - {e}")
        return None


async def download_asset_files(
    assets: list[Assets],
    download_dir: Path,
) -> list[Assets]:
    logger.info("Downloading files...")

    valid_assets: list[Assets] = []

    with start_blocking_portal() as portal:
        futures = [
            portal.start_task_soon(
                _download_and_confirm_asset,
                download_dir,
                asset,
            )
            for asset in assets
        ]

        for future in as_completed(futures):
            result = future.result()
            if result is not None:
                valid_assets.append(result)

    return valid_assets


async def process_servant_data(
    servant_data: list[ServantData],
    local_data: ServantDataIndexed,
    debug: bool = False,
):
    logger.info("Processing servant data...")

    debug_index = 0

    for latest_data in servant_data:
        if debug and debug_index >= 5:
            break

        servant_directory_name = f"{latest_data.idx:04d}"

        temp_download_dir = TEMP_SERVANT_DIR / servant_directory_name
        temp_download_dir.mkdir(exist_ok=True, parents=True)

        rename_txt_file = False
        new_assets_found = False

        local_entry = local_data.get(latest_data.idx, None)
        if local_entry is None:
            logger.info(f"New servant data found: {latest_data.name}")

            new_assets_found = True
            latest_data.assets = await download_asset_files(
                latest_data.assets,
                temp_download_dir,
            )

        else:
            if local_entry.sanitized_name != latest_data.sanitized_name:
                rename_txt_file = True

            if len(local_entry.assets) != len(latest_data.assets):
                logger.info(f"Updating {latest_data.name} assets...")
                new_assets_found = True
                latest_data.assets = await download_asset_files(
                    latest_data.assets,
                    temp_download_dir,
                )
        output_dir = OUTPUT_SERVANT_DIR / servant_directory_name
        output_dir.mkdir(exist_ok=True, parents=True)

        output_color_dir = OUTPUT_SERVANT_COLOR_DIR / servant_directory_name
        output_color_dir.mkdir(exist_ok=True, parents=True)

        txt_file_path = f"{latest_data.sanitized_name}.txt"

        if rename_txt_file or new_assets_found:
            (output_dir / txt_file_path).touch(exist_ok=True)
            (output_color_dir / txt_file_path).touch(exist_ok=True)

        if new_assets_found:
            await to_thread.run_sync(
                image.create_support_servant_img,
                temp_download_dir,
                output_dir / "support.png",
                output_color_dir / "support.png",
            )

            logger.info(f"Servant images created for: {latest_data.sanitized_name}")

        if debug:
            debug_index += 1
        else:
            # Wait for 1 second to avoid overwhelming the server
            # with too many requests
            await asyncio.sleep(1)

    if not debug:
        await write_json(
            LOCAL_SERVANT_DATA,
            servant_data,
        )


async def process_craft_essence_data(
    ce_data: list[CraftEssenceData],
    local_data: CraftEssenceDataIndexed,
    debug: bool = False,
):
    logger.info("Processing craft essence data...")

    debug_index = 0

    for latest_data in ce_data:
        if debug and debug_index >= 5:
            break

        local_entry = local_data.get(latest_data.idx, None)
        if local_entry is None:
            logger.info(f"New craft essence data found: {latest_data.name}")
            # Download the assets for the new craft essence
        else:
            logger.info(f"Updating craft essence data: {latest_data.name}")

        if debug:
            debug_index += 1
