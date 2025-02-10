from pathlib import Path
import process
import image

CWD = Path(__file__).parent


def main():
    other_repository_dir = CWD / "fga-support"
    if not other_repository_dir.exists():
        return

    # Read the old data and compare with the new data
    process.process_data()

    input_directory = CWD / "input"

    output_directory = CWD / "output"

    for servant_dir in input_directory.iterdir():
        if servant_dir.is_dir():
            output_servant_dir = output_directory / servant_dir.name
            output_servant_dir.mkdir(exist_ok=True, parents=True)

            image.combine_images(
                image_dir=servant_dir,
                output_dir=output_servant_dir,
            )

    # Move the images to the other repository
    output_directory.rename(other_repository_dir / "servant")


if __name__ == "__main__":
    main()
