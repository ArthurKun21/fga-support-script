from pathlib import Path

from anyio import create_task_group, open_file
from loguru import logger

from enums import SupportKind
from models import (
    Assets,
    CraftEssenceData,
    CraftEssenceDataIndexed,
    ServantData,
    ServantDataIndexed,
)
from utils import download_file

ROOT = Path(__file__).cwd()

TMP_DIR = ROOT / "tmp"
TMP_DIR.mkdir(exist_ok=True, parents=True)

SERVANT = SupportKind.SERVANT.value
CE = SupportKind.CRAFT_ESSENCE.value

TEMP_SERVANT_DIR = TMP_DIR / SERVANT
TEMP_SERVANT_DIR.mkdir(exist_ok=True, parents=True)

TEMP_CE_DIR = TMP_DIR / CE
TEMP_CE_DIR.mkdir(exist_ok=True, parents=True)


async def download_files(
    assets: list[Assets],
    download_dir: Path,
    debug: bool = False,
):
    logger.info("Downloading files...")

    async with create_task_group() as tg:
        for asset in assets:
            tg.start_soon(
                download_file,
                asset.url,
                download_dir / asset.url_file_name,
                debug,
            )


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

        temp_download_dir = TEMP_SERVANT_DIR / f"{latest_data.idx:04d}"
        temp_download_dir.mkdir(exist_ok=True, parents=True)

        txt_name_file_path = temp_download_dir / f"{latest_data.sanitized_name}.txt"
        if not txt_name_file_path.exists():
            async with await open_file(txt_name_file_path, "w", encoding="utf-8"):
                pass

        rename_txt_file = False
        new_assets_found = False

        local_entry = local_data.get(latest_data.idx, None)
        if local_entry is None:
            logger.info(f"New servant data found: {latest_data.name}")

            new_assets_found = True
            await download_files(
                latest_data.assets,
                temp_download_dir,
                debug=debug,
            )

        else:
            if local_entry.sanitized_name != latest_data.sanitized_name:
                rename_txt_file = True

            if len(local_entry.assets) != len(latest_data.assets):
                logger.info("Downloading assets...")
                new_assets_found = True
                await download_files(
                    latest_data.assets,
                    temp_download_dir,
                    debug=debug,
                )

        if rename_txt_file:
            pass

        if new_assets_found:
            pass

        if debug:
            debug_index += 1


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
