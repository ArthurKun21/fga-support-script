from pathlib import Path

import cv2
import numpy as np
from PIL import Image

IMAGE_EXTENSIONS = [".png", ".jpg", ".jpeg"]


def crop_file(input_file: Path) -> np.ndarray:
    with Image.open(input_file) as img:
        img = img.resize(size=(157, 157), resample=Image.Resampling.LANCZOS)

        x = 3
        y = 47
        width = 157
        height = 50

        box = (x, y, x + width, y + height)

        cropped_img = img.crop(box)

    img_np = np.array(cropped_img)

    return img_np


def combine_crop_np(crop_image_list: list[np.ndarray]) -> np.ndarray:
    combined_img = np.concatenate(crop_image_list, axis=0)
    return combined_img


def combine_images(
    image_dir: Path,
    output_dir: Path,
):
    images = [
        i for i in image_dir.iterdir() if i.is_file() and i.suffix in IMAGE_EXTENSIONS
    ]

    if len(images) == 0:
        print(f"No images found in {image_dir.name}")
        return

    text_files = [i for i in image_dir.iterdir() if i.is_file() and i.suffix == ".txt"]
    if len(text_files) == 0:
        print(f"No txt file found in {image_dir.name}")
        return
    file_name = text_files[0].stem
    print(f"Name: {file_name}\tImages: {len(images)}")

    crop_image_list = [crop_file(i) for i in images]
    combined_img = combine_crop_np(crop_image_list)

    output_file = output_dir / f"{file_name}.png"
    cv2.imwrite(str(output_file), cv2.cvtColor(combined_img, cv2.COLOR_RGB2GRAY))
