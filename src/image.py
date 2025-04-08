from pathlib import Path

import cv2
from cv2.typing import MatLike
from loguru import logger

IMG_EXT = {".jpg", ".jpeg", ".png"}


def create_support_servant_img(
    source_dir: Path,
    dest_file_path: Path,
    dest_color_file_path: Path,
):
    image_np_list = _read_images(source_dir)
    final_image = _process_servant_images(image_np_list)

    cv2.imwrite(str(dest_color_file_path), final_image)

    final_image_np = cv2.cvtColor(final_image.copy(), cv2.COLOR_BGR2GRAY)
    cv2.imwrite(str(dest_file_path), final_image_np)
    logger.info("Images processed and saved successfully.")


def create_support_ce_img(
    source_dir: Path,
    dest_file_path: Path,
    dest_color_file_path: Path,
):
    image_np_list = _read_images(source_dir)

    if len(image_np_list) == 0:
        logger.error(f"No images found in the directory: {source_dir}")
        return

    image_np = image_np_list[0]

    cv2.imwrite(str(dest_color_file_path), image_np)

    image_np_gray = cv2.cvtColor(image_np.copy(), cv2.COLOR_BGR2GRAY)
    cv2.imwrite(str(dest_file_path), image_np_gray)
    logger.info("CE Image processed and saved successfully.")


def _process_servant_images(
    image_np_list: list[MatLike],
) -> MatLike:
    """
    Process a list of images and return a combined image.
    This function resizes each image to a fixed size and crops a specific region
    from each image. The cropped images are then concatenated vertically.

    Args:
        image_np_list (list[MatLike]): A list of numpy arrays representing the images.

    Returns:
        MatLike: A combined image as a numpy array.
    """
    new_image_np_list: list[MatLike] = []
    for image in image_np_list:
        resize_image = cv2.resize(
            image,
            (157, 157),
            interpolation=cv2.INTER_LANCZOS4,
        )

        x = 3
        y = 47
        width = 157
        height = 50

        cropped_image = resize_image[y : y + height, x : x + width]
        new_image_np_list.append(cropped_image)

    combined_img = cv2.vconcat(new_image_np_list)
    return combined_img


def _read_images(
    source_dir: Path,
) -> list[MatLike]:
    """ "
    Read images from a directory and return them as a list of numpy arrays.
    This function iterates through all files in the specified directory,
    checks if they are valid image files based on their extensions,
    and reads them into numpy arrays using OpenCV.
    If a file is not a valid image or cannot be read, it is skipped.

    Args:
        source_dir (Path): The directory containing the images to be read.

    Returns:
        list[MatLike]: A list of numpy arrays representing the images.
    """
    image_np_list: list[MatLike] = []

    images: list[Path] = []
    for ext in IMG_EXT:
        images.extend(source_dir.glob(f"**/*{ext}"))
    images = sorted(images)

    for img_path in images:
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
