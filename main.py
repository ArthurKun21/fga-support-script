import shutil
from pathlib import Path

import image
import process

CWD = Path(__file__).parent


def main():
    other_repository_dir_path = CWD / "fga-support"
    if not other_repository_dir_path.exists():
        print("The other repository was not found.")
        return

    alt_repository_dir = CWD / "fga-old-support"

    input_dir_path = CWD / "input"

    output_dir_path = CWD / "output"

    # Read the old data and compare with the new data
    process.process_servant_data()

    alternative_dir_path = CWD / "alternative"

    servant_dir_path = input_dir_path / "servant"

    for input_servant_dir in servant_dir_path.iterdir():
        if input_servant_dir.is_dir():
            output_servant_dir_path = output_dir_path / input_servant_dir.name
            output_servant_dir_path.mkdir(exist_ok=True, parents=True)

            image.combine_images(
                image_dir=input_servant_dir,
                output_dir=output_servant_dir_path,
            )

            alt_servant_dir = alternative_dir_path / input_servant_dir.name
            alt_servant_dir.mkdir(exist_ok=True, parents=True)
            image.combine_images(
                image_dir=input_servant_dir,
                output_dir=alt_servant_dir,
                combine=False,
            )

    # Move the images to the other repository
    try:
        target_directory = other_repository_dir_path / "servant"
        shutil.copytree(
            output_dir_path,
            target_directory,
            dirs_exist_ok=True,
        )
    except FileExistsError:
        print("The other repository already has the images.")

    try:
        if alt_repository_dir.exists():
            alt_target_directory = alt_repository_dir / "servant"
            shutil.copytree(
                alternative_dir_path,
                alt_target_directory,
                dirs_exist_ok=True,
            )
    except FileExistsError:
        print("The alternative repository already has the images.")


if __name__ == "__main__":
    main()
