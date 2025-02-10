from pathlib import Path

CWD = Path(__file__).parent

INPUT_DIR_PATH = CWD / "input"
OUTPUT_DIR_PATH = CWD / "output"


def main():
    # Servant
    output_servant_dir = OUTPUT_DIR_PATH / "servant"
    output_servant_dir.mkdir(parents=True, exist_ok=True)

    # craft_essence
    output_craft_essence_dir = OUTPUT_DIR_PATH / "craft_essence"
    output_craft_essence_dir.mkdir(parents=True, exist_ok=True)


if __name__ == "__main__":
    main()
