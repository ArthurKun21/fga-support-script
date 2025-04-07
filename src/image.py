from pathlib import Path

import cv2
import numpy as np
from loguru import logger
from numpy.typing import ArrayLike

IMG_EXT = {".jpg", ".jpeg", ".png"}


def create_support_servant_img(
    source_dir: Path,
    dest_file_path: Path,
    dest_color_file_path: Path,
    debug: bool = False,
):
    if debug:
        logger.debug("Debug mode is enabled. Assumed to be successful.")
        with open(dest_file_path, "wb"):
            pass
        with open(dest_color_file_path, "wb"):
            pass
        return

    image_np_list = _read_images(source_dir)
    final_image = _process_servant_images(image_np_list)

    final_image_np = np.array(final_image)

    cv2.imwrite(str(dest_color_file_path), final_image_np)

    final_image_np = cv2.cvtColor(final_image_np.copy(), cv2.COLOR_BGR2GRAY)
    cv2.imwrite(str(dest_file_path), final_image_np)
    logger.info("Images processed and saved successfully.")


def _process_servant_images(
    image_np_list: list[ArrayLike],
) -> ArrayLike:
    """
    Process a list of images and return a combined image.
    This function resizes each image to a fixed size and crops a specific region
    from each image. The cropped images are then concatenated vertically.

    Args:
        image_np_list (list[ArrayLike]): A list of numpy arrays representing the images.

    Returns:
        ArrayLike: A combined image as a numpy array.
    """
    new_image_np_list: list[ArrayLike] = []
    for image in image_np_list:
        image_np = np.array(image)

        resize_image = cv2.resize(
            image_np,
            (157, 157),
            interpolation=cv2.INTER_LANCZOS4,
        )

        x = 3
        y = 47
        width = 157
        height = 50

        cropped_image = resize_image[y : y + height, x : x + width]
        new_image_np_list.append(cropped_image)

    combined_img = np.concatenate(new_image_np_list, axis=0)
    return combined_img


def _read_images(
    source_dir: Path,
) -> list[ArrayLike]:
    """ "
    Read images from a directory and return them as a list of numpy arrays.
    This function iterates through all files in the specified directory,
    checks if they are valid image files based on their extensions,
    and reads them into numpy arrays using OpenCV.
    If a file is not a valid image or cannot be read, it is skipped.

    Args:
        source_dir (Path): The directory containing the images to be read.

    Returns:
        list[ArrayLike]: A list of numpy arrays representing the images.
    """
    image_np_list: list[ArrayLike] = []

    for img_path in source_dir.iterdir():
        if not img_path.is_file():
            continue

        if img_path.suffix not in IMG_EXT:
            logger.warning(f"Invalid file: {img_path.name}")
            continue

        try:
            image_np = cv2.imread(str(img_path))
            if image_np is None or image_np.size == 0:
                logger.warning(f"Failed to read image: {img_path.name}")
                continue

            image_np_list.append(image_np)

        except Exception as e:
            logger.error(f"Error reading image {img_path.name}: {e}")
            continue

    return image_np_list
