import asyncio
from collections.abc import Callable
from pathlib import Path

import cv2
from anyio import create_task_group, to_thread
from loguru import logger

from config import app_config
from constants import (
    LOCAL_CE_DATA,
    LOCAL_SERVANT_DATA,
    OUTPUT_CE_COLOR_DIR,
    OUTPUT_CE_DIR,
    OUTPUT_SERVANT_COLOR_DIR,
    OUTPUT_SERVANT_DIR,
    TEMP_CE_DIR,
)
from enums import SupportKind
from image import create_support_ce_img, create_support_servant_img
from models import (
    Assets,
    BaseData,
    CraftEssenceData,
    ServantData,
)
from utils import download_file, write_json

type IndexedT = dict[int, BaseData]


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
    assets: list[Assets], download_dir: Path, kind: SupportKind
) -> list[Assets]:
    logger.info(
        f"{kind.value.upper()} {download_dir.name} - Downloading and verifying files..."
    )

    results: list[Assets | None] = []

    async def _download_task(asset: Assets):
        result = await _download_and_confirm_asset(download_dir, asset)
        results.append(result)

    try:
        async with create_task_group() as tg:
            for asset in assets:
                tg.start_soon(_download_task, asset)
    except Exception as e:
        logger.error(f"Error downloading assets: {e}")

    valid_assets: list[Assets] = [asset for asset in results if asset is not None]

    valid_assets = sorted(valid_assets, key=lambda x: x.key)

    return valid_assets


async def process_servant_data(
    servant_data: list[ServantData],
    local_data: IndexedT,
    debug: bool = False,
    dry_run: bool = False,
):
    await _process_generic_data(
        latest_data_list=servant_data,
        local_data=local_data,
        kind=SupportKind.SERVANT,
        temp_dir=app_config.directories.tmp_dir,
        output_dir_base=OUTPUT_SERVANT_DIR,
        output_color_dir_base=OUTPUT_SERVANT_COLOR_DIR,
        image_creation_func=create_support_servant_img,
        output_image_filename="support.png",
        local_data_path=LOCAL_SERVANT_DATA,
        debug=debug,
        dry_run=dry_run,
    )


async def process_craft_essence_data(
    ce_data: list[CraftEssenceData],
    local_data: IndexedT,
    debug: bool = False,
    dry_run: bool = False,
):
    await _process_generic_data(
        latest_data_list=ce_data,
        local_data=local_data,
        kind=SupportKind.CRAFT_ESSENCE,
        temp_dir=TEMP_CE_DIR,
        output_dir_base=OUTPUT_CE_DIR,
        output_color_dir_base=OUTPUT_CE_COLOR_DIR,
        image_creation_func=create_support_ce_img,
        output_image_filename="ce.png",
        local_data_path=LOCAL_CE_DATA,
        debug=debug,
        dry_run=dry_run,
    )


async def _process_generic_data(
    latest_data_list: list[BaseData],
    local_data: IndexedT,
    kind: SupportKind,
    temp_dir: Path,
    output_dir_base: Path,
    output_color_dir_base: Path,
    image_creation_func: Callable[[Path, Path, Path], None],
    output_image_filename: str,
    local_data_path: Path,
    debug: bool = False,
    dry_run: bool = False,
):
    logger.info(f"Processing {kind.value} data...")
    debug_index = 0
    updated_data_list: list[BaseData] = []

    for latest_data in latest_data_list:
        if (debug or dry_run) and debug_index >= 5:
            updated_data_list.append(latest_data)
            continue

        directory_name = f"{latest_data.idx:04d}"
        temp_download_dir = temp_dir / directory_name
        temp_download_dir.mkdir(exist_ok=True, parents=True)

        rename_txt_file = False
        new_assets_found = False

        local_entry = local_data.get(latest_data.idx)

        if local_entry is None:
            logger.info(
                f"New {kind.value} data found: {latest_data.idx:04d} {latest_data.name}"
            )
            new_assets_found = True
        else:
            if local_entry.sanitized_name != latest_data.sanitized_name:
                rename_txt_file = True
            if len(local_entry.assets) != len(latest_data.assets):
                logger.info(
                    f"Updating {latest_data.idx:04d} {latest_data.name} assets..."
                )
                new_assets_found = True

        if new_assets_found:
            # Download only if new or assets changed
            downloaded_assets = await download_asset_files(
                latest_data.assets,  # Use the latest asset list for download
                temp_download_dir,
                kind,
            )
            # Update the data object with the successfully downloaded assets
            latest_data.assets = downloaded_assets

        output_dir = output_dir_base / directory_name
        output_dir.mkdir(exist_ok=True, parents=True)
        output_color_dir = output_color_dir_base / directory_name
        output_color_dir.mkdir(exist_ok=True, parents=True)

        txt_file_path = output_dir / f"{latest_data.sanitized_name}.txt"
        color_txt_file_path = output_color_dir / f"{latest_data.sanitized_name}.txt"

        if rename_txt_file or new_assets_found:
            txt_file_path.touch(exist_ok=True)
            color_txt_file_path.touch(exist_ok=True)

        if new_assets_found:
            await to_thread.run_sync(
                image_creation_func,
                temp_download_dir,
                output_dir / output_image_filename,
                output_color_dir / output_image_filename,
            )
            logger.info(
                f"{kind.value.capitalize()} images created for: "
                f"{latest_data.idx:04d} {latest_data.sanitized_name}"
            )
            await asyncio.sleep(0.5)

        updated_data_list.append(latest_data)  # Add processed/updated data

        if debug or dry_run:
            debug_index += 1

    if not debug and not dry_run:
        # Write the potentially modified list back (includes updated asset lists)
        await write_json(local_data_path, updated_data_list)
