import shutil
from pathlib import Path

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

    legacy_dir_path = CWD / "legacy"

    servant_raw_path = input_dir_path / "servant"
    servant_raw_path.mkdir(exist_ok=True, parents=True)

    new_processed_path = output_dir_path / "servant"
    new_processed_path.mkdir(exist_ok=True, parents=True)

    legacy_processed_path = legacy_dir_path / "servant"
    legacy_processed_path.mkdir(exist_ok=True, parents=True)

    for input_servant_dir in servant_raw_path.iterdir():
        if input_servant_dir.is_dir():
            try:
                output_servant_dir = new_processed_path / input_servant_dir.name
                output_servant_dir.mkdir(exist_ok=True, parents=True)

                image.process_servant(
                    image_dir=input_servant_dir,
                    output_dir=output_servant_dir,
                )
            except Exception as e:
                print(f"Error combining images: {e}")

            try:
                legacy_servant_dir = legacy_processed_path / input_servant_dir.name
                legacy_servant_dir.mkdir(exist_ok=True, parents=True)
                image.process_servant(
                    image_dir=input_servant_dir,
                    output_dir=legacy_servant_dir,
                    combine=False,
                )
            except Exception as e:
                print(f"Error combining legacy images: {e}")

    # Move the images to the other repository
    try:
        target_directory = main_repository_dir_path / "servant"
        shutil.copytree(
            new_processed_path,
            target_directory,
            dirs_exist_ok=True,
        )
    except FileExistsError:
        print("The other repository already has the images.")
    except FileNotFoundError:
        print("The other repository was not found.")
    except Exception as e:
        print(f"Error moving images to the other repository: {e}")

    try:
        if alt_repository_dir.exists():
            alt_target_directory = alt_repository_dir / "servant"
            shutil.copytree(
                legacy_processed_path,
                alt_target_directory,
                dirs_exist_ok=True,
            )
    except FileExistsError:
        print("The alternative repository already has the images.")
    except FileNotFoundError:
        print("The alternative repository was not found.")
    except Exception as e:
        print(f"Error moving images to the alternative repository: {e}")


def main():
    main_repository_dir_path = CWD / "fga-support"
    if not main_repository_dir_path.exists():
        print("The other repository was not found.")
        return

    alt_repository_dir = CWD / "fga-old-support"

    input_dir_path = CWD / "input"

    output_dir_path = CWD / "output"

    servant(
        input_dir_path=input_dir_path,
        output_dir_path=output_dir_path,
        main_repository_dir_path=main_repository_dir_path,
        alt_repository_dir=alt_repository_dir,
    )


if __name__ == "__main__":
    main()
