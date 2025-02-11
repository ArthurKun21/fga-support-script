import shutil
from pathlib import Path

import argparse
import image
import process

CWD = Path(__file__).parent


def servant(
    input_dir_path: Path,
    output_dir_path: Path,
    main_repository_dir_path: Path,
    alt_repository_dir: Path,
):
    """Process servant images and data according to specified paths.
    This function processes servant data and combines servant images from a source directory
    to output directories, including a legacy directory. It handles both combined and
    individual image processing.
    Args:
        input_dir_path (Path): Directory path containing the input servant data and images
        output_dir_path (Path): Directory path where processed combined images will be saved
        main_repository_dir_path (Path): Main repository directory path (currently unused)
        alt_repository_dir (Path): Alternative repository directory path (currently unused)
    Raises:
        Exception: If there are errors during image combination process, exceptions will be caught
                  and error messages printed
    Notes:
        - Creates output directories if they don't exist
        - Processes both combined and legacy (uncombined) images
        - Skips non-directory entries in the servant directory
        - Uses process.process_servant_data() for data processing
        - Legacy images are stored separately without combining
    """

    # Read the old data and compare with the new data
    process.process_servant_data()

    dir_name = "servant"

    legacy_dir_path = CWD / "legacy"

    paths = {
        "input": input_dir_path / dir_name,
        "output": output_dir_path / dir_name,
        "legacy": legacy_dir_path / dir_name,
        "main": main_repository_dir_path / dir_name,
        "alt": alt_repository_dir / dir_name,
        "output-colored": output_dir_path / f"{dir_name}-colored",
        "legacy-colored": legacy_dir_path / f"{dir_name}-colored",
        "main-colored": main_repository_dir_path / f"{dir_name}-colored",
        "alt-colored": alt_repository_dir / f"{dir_name}-colored",
    }
    for path in paths.values():
        path.mkdir(exist_ok=True, parents=True)

    for input_servant_dir in paths["input"].iterdir():
        if not input_servant_dir.is_dir():
            continue

        for process_types in [
            ("new", paths["output"], True),
            ("legacy", paths["legacy"], False),
            ("new-colored", paths["output-colored"], True),
            ("legacy-colored", paths["legacy-colored"], False),
        ]:
            output_servant_dir = process_types[1] / input_servant_dir.name
            output_servant_dir.mkdir(exist_ok=True, parents=True)

            try:
                image.process_servant(
                    image_dir=input_servant_dir,
                    output_dir=output_servant_dir,
                    combine=process_types[2],
                    is_colored="colored" in process_types[1].name,
                )
            except Exception as e:
                print(f"Error combining images: {e}")

    for target in [
        ("main", paths["output"], paths["main"]),
        ("alt", paths["legacy"], paths["alt"]),
        ("main-colored", paths["output-colored"], paths["main-colored"]),
        ("alt-colored", paths["legacy-colored"], paths["alt-colored"]),
    ]:
        if "alt" in target[0] and not alt_repository_dir.exists():
            continue

        try:
            shutil.copytree(
                target[1],
                target[2],
                dirs_exist_ok=True,
            )
        except FileExistsError:
            print(f"The {target[0]} repository already has the images.")
        except FileNotFoundError:
            print(f"The {target[0]} repository was not found.")
        except Exception as e:
            print(f"Error moving images to the {target[0]} repository: {e}")


def craft_essence(
    input_dir_path: Path,
    output_dir_path: Path,
    main_repository_dir_path: Path,
    alt_repository_dir: Path,
):
    # Read the old data and compare with the new data
    process.process_craft_essence_data()

    dir_name = "craft_essence"

    legacy_dir_path = CWD / "legacy"

    paths = {
        "input": input_dir_path / dir_name,
        "output": output_dir_path / dir_name,
        "legacy": legacy_dir_path / dir_name,
        "main": main_repository_dir_path / dir_name,
        "alt": alt_repository_dir / dir_name,
        "output-colored": output_dir_path / f"{dir_name}-colored",
        "legacy-colored": legacy_dir_path / f"{dir_name}-colored",
        "main-colored": main_repository_dir_path / f"{dir_name}-colored",
        "alt-colored": alt_repository_dir / f"{dir_name}-colored",
    }
    for path in paths.values():
        path.mkdir(exist_ok=True, parents=True)

    for input_ce_dir in paths["input"].iterdir():
        if not input_ce_dir.is_dir():
            continue

        for process_types in [
            ("new", paths["output"] / input_ce_dir.name, True),
            ("legacy", paths["legacy"], False),
            ("new-colored", paths["output-colored"] / input_ce_dir.name, True),
            ("legacy-colored", paths["legacy-colored"], False),
        ]:
            process_types[1].mkdir(exist_ok=True, parents=True)
            try:
                image.process_craft_essence(
                    image_dir=input_ce_dir,
                    output_dir=process_types[1],
                    is_new=process_types[2],
                    is_colored="colored" in process_types[0],
                )
            except Exception as e:
                print(f"Error combining images: {e}")

    for target in [
        ("main", paths["output"], paths["main"]),
        ("alt", paths["legacy"], paths["alt"]),
        ("main-colored", paths["output-colored"], paths["main-colored"]),
        ("alt-colored", paths["legacy-colored"], paths["alt-colored"]),
    ]:
        if "alt" in target[0] and not alt_repository_dir.exists():
            continue

        try:
            shutil.copytree(
                target[1],
                target[2],
                dirs_exist_ok=True,
            )
        except FileExistsError:
            print(f"The {target[0]} repository already has the images.")
        except FileNotFoundError:
            print(f"The {target[0]} repository was not found.")
        except Exception as e:
            print(f"Error moving images to the {target[0]} repository: {e}")


def parse_args():
    parser = argparse.ArgumentParser(description="FGO support automation script")
    parser.add_argument("--servant", action="store_true", help="Process servant images")
    parser.add_argument(
        "--delete", action="store_true", help="Delete the output Repository"
    )
    return parser.parse_args()


def main():
    args = parse_args()

    main_repository_dir_path = CWD / "fga-support"
    if not main_repository_dir_path.exists():
        print("The other repository was not found.")
        return

    alt_repository_dir = CWD / "fga-old-support"

    if args.delete:
        try:
            for directory in [
                main_repository_dir_path / "servant",
                main_repository_dir_path / "servant-colored",
                main_repository_dir_path / "craft_essence",
                main_repository_dir_path / "craft_essence-colored",
                alt_repository_dir / "servant",
                alt_repository_dir / "servant-colored",
                alt_repository_dir / "craft_essence",
                alt_repository_dir / "craft_essence-colored",
            ]:
                if directory.exists():
                    for item in directory.iterdir():
                        if item.is_file():
                            item.unlink()
                        elif item.is_dir():
                            shutil.rmtree(item)
        except Exception as e:
            print(f"Error deleting the output Repository: {e}")
        return

    input_dir_path = CWD / "input"

    output_dir_path = CWD / "output"

    if args.servant:
        servant(
            input_dir_path=input_dir_path,
            output_dir_path=output_dir_path,
            main_repository_dir_path=main_repository_dir_path,
            alt_repository_dir=alt_repository_dir,
        )
    else:
        craft_essence(
            input_dir_path=input_dir_path,
            output_dir_path=output_dir_path,
            main_repository_dir_path=main_repository_dir_path,
            alt_repository_dir=alt_repository_dir,
        )


if __name__ == "__main__":
    main()
