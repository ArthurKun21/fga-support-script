from pathlib import Path

from enums import SupportKind

ROOT = Path(__file__).cwd()

TMP_DIR = ROOT / "tmp"
TMP_DIR.mkdir(exist_ok=True, parents=True)

SERVANT = SupportKind.SERVANT.value
CE = SupportKind.CRAFT_ESSENCE.value

TEMP_SERVANT_DIR = TMP_DIR / SERVANT
TEMP_SERVANT_DIR.mkdir(exist_ok=True, parents=True)

TEMP_CE_DIR = TMP_DIR / CE
TEMP_CE_DIR.mkdir(exist_ok=True, parents=True)

OUTPUT_DIR = ROOT / "output"
OUTPUT_DIR.mkdir(exist_ok=True, parents=True)

OUTPUT_SERVANT_DIR = OUTPUT_DIR / SERVANT
OUTPUT_SERVANT_DIR.mkdir(exist_ok=True, parents=True)

OUTPUT_SERVANT_COLOR_DIR = OUTPUT_DIR / f"{SERVANT}-color"
OUTPUT_SERVANT_COLOR_DIR.mkdir(exist_ok=True, parents=True)

OUTPUT_CE_DIR = OUTPUT_DIR / CE
OUTPUT_CE_DIR.mkdir(exist_ok=True, parents=True)

OUTPUT_CE_COLOR_DIR = OUTPUT_DIR / f"{CE}-color"
OUTPUT_CE_COLOR_DIR.mkdir(exist_ok=True, parents=True)

DATA_DIR = ROOT / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

REMOTE_CE_DATA = DATA_DIR / f"{CE}.json"
REMOTE_SERVANT_DATA = DATA_DIR / f"{SERVANT}.json"

LOCAL_CE_DATA = ROOT / f"{CE}.json"
LOCAL_SERVANT_DATA = ROOT / f"{SERVANT}.json"
