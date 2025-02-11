from pathlib import Path
import process
import image
import shutil

CWD = Path(__file__).parent


def main():
    other_repository_dir_path = CWD / "fga-support"
    if not other_repository_dir_path.exists():
        print("The other repository was not found.")
        return

    # Read the old data and compare with the new data
    process.process_data()

    input_dir_path = CWD / "input"

    output_dir_path = CWD / "output"

    alternative_dir_path = CWD / "alternative"

    for servant_dir in input_dir_path.iterdir():
        if servant_dir.is_dir():
            output_servant_dir_path = output_dir_path / servant_dir.name
            output_servant_dir_path.mkdir(exist_ok=True, parents=True)

            image.combine_images(
                image_dir=servant_dir,
                output_dir=output_servant_dir_path,
            )

            alt_servant_dir = alternative_dir_path / servant_dir.name
            alt_servant_dir.mkdir(exist_ok=True, parents=True)
            image.combine_images(
                image_dir=servant_dir,
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
        alt_repository_dir = CWD / "fga-old-support"
        if alt_repository_dir.exists():
            alt_target_directory = alt_repository_dir / "alternative"
            shutil.copytree(
                alternative_dir_path,
                alt_target_directory,
                dirs_exist_ok=True,
            )
    except FileExistsError:
        print("The alternative repository already has the images.")


if __name__ == "__main__":
    main()
