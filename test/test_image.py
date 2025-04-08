from pathlib import Path
from unittest import mock

import cv2
import numpy as np
import pytest

from image import _read_images, create_support_servant_img

dir_path = Path(__file__).parent / "images"

servant_dir = dir_path / "servant"

servant_input_dir = servant_dir / "input"

servant_output_file = servant_dir / "output.png"

servant_support_file = servant_dir / "support.png"


@pytest.fixture
def sample_image():
    """Create a simple sample image for testing."""
    return np.ones((100, 100, 3), dtype=np.uint8) * 255


def test_read_images_empty_dir(tmp_path):
    """Test reading from an empty directory."""
    result = _read_images(tmp_path)
    assert isinstance(result, list)
    assert len(result) == 0


def test_read_images_valid_images(tmp_path, sample_image):
    """Test reading valid image files."""
    # Create sample images
    for i, ext in enumerate([".jpg", ".jpeg", ".png"]):
        img_path = tmp_path / f"test{i}{ext}"
        cv2.imwrite(str(img_path), sample_image)

    result = _read_images(tmp_path)

    assert len(result) == 3
    for img in result:
        assert isinstance(img, np.ndarray)
        assert img.shape[0] == 100
        assert img.shape[1] == 100
        assert img.shape[2] == 3


def test_read_images_invalid_extension(tmp_path, sample_image):
    """Test with invalid file extensions."""
    # Create valid image
    cv2.imwrite(str(tmp_path / "valid.jpg"), sample_image)

    # Create file with invalid extension
    with open(str(tmp_path / "invalid.txt"), "w") as f:
        f.write("not an image")

    result = _read_images(tmp_path)
    assert len(result) == 1


def test_read_images_mixed_files(tmp_path, sample_image):
    """Test with mixture of valid and invalid files."""
    # Create valid images
    cv2.imwrite(str(tmp_path / "valid1.jpg"), sample_image)
    cv2.imwrite(str(tmp_path / "valid2.png"), sample_image)

    # Create invalid files
    with open(str(tmp_path / "invalid.txt"), "w") as f:
        f.write("not an image")

    # Create directory (not a file)
    (tmp_path / "subdir").mkdir()

    result = _read_images(tmp_path)
    assert len(result) == 2


@mock.patch("cv2.imread")
def test_read_images_failed_read(mock_imread, tmp_path):
    """Test handling of images that fail to read."""
    mock_imread.return_value = None

    # Create image files that will "fail" to read due to our mock
    for ext in [".jpg", ".png"]:
        img_path = tmp_path / f"test{ext}"
        with open(img_path, "wb") as f:
            f.write(b"dummy data")

    result = _read_images(tmp_path)
    assert len(result) == 0
    assert mock_imread.call_count == 2


def test_read_images_error_handling(tmp_path):
    """Test error handling when reading images."""
    with mock.patch("cv2.imread", side_effect=Exception("Test error")):
        # Create an image file
        img_path = tmp_path / "test.jpg"
        with open(img_path, "wb") as f:
            f.write(b"dummy data")

        result = _read_images(tmp_path)
        assert len(result) == 0


class TestRealImage:
    def test_output_np_is_valid(self):
        output_np = cv2.imread(str(servant_output_file))

        assert output_np is not None, "Output image should not be None"
        assert output_np.size > 0, "Output image should not be empty"

        assert output_np.shape[0] == 250, "Output image height should be 250"
        assert output_np.shape[1] == 157, "Output image width should be 157"
        assert output_np.ndim == 3, (
            "Output image should have 3 dimensions (height, width, channels)"
        )

    def test_support_is_valid(self):
        """Test the creation of support servant image."""
        # Read the output image
        support_np = cv2.imread(str(servant_support_file))

        assert support_np is not None, "Output image should not be None"
        assert support_np.size > 0, "Output image should not be empty"

        assert support_np.shape[0] == 44, "Output image height should be 44"
        assert support_np.shape[1] == 125, "Output image width should be 125"
        assert support_np.ndim == 3, (
            "Output image should have 3 dimensions (height, width, channels)"
        )

    def create_support_servant(self, tmp_path) -> tuple[Path, Path]:
        color_file_path = tmp_path / "color_output.png"
        gray_file_path = tmp_path / "gray_output.png"

        create_support_servant_img(
            servant_input_dir,
            gray_file_path,
            color_file_path,
        )

        return color_file_path, gray_file_path

    def test_create_support_servant_gray(self, tmp_path):
        """Test the creation of gray image."""
        _, gray_file_path = self.create_support_servant(tmp_path)

        # Read the gray
        gray_image = cv2.imread(str(gray_file_path), cv2.IMREAD_GRAYSCALE)
        assert gray_image is not None, "Gray image should not be None"
        assert gray_image.size > 0, "Gray image should not be empty"

        assert gray_image.shape[0] == 250, "Gray image height should be 250"
        assert gray_image.shape[1] == 157, "Gray image width should be 157"

        # Read the output image
        output_np = cv2.imread(str(servant_output_file), cv2.IMREAD_GRAYSCALE)

        # Template matching the gray and the output image
        result = cv2.matchTemplate(gray_image, output_np, cv2.TM_CCOEFF_NORMED)

        assert result is not None, "Template matching result should not be None"

        _, max_val, _, _ = cv2.minMaxLoc(result)

        assert max_val > 0.8, "Template matching should have a high correlation"
        assert max_val < 1.0, "Template matching should not be perfect (due to noise)"

    def test_create_support_servant_color(self, tmp_path):
        """Test the creation of color image."""
        color_file_path, _ = self.create_support_servant(tmp_path)

        # Read the output image
        output_np = cv2.imread(str(servant_output_file), cv2.IMREAD_GRAYSCALE)

        # Read the color image as gray
        color_image = cv2.imread(str(color_file_path), cv2.IMREAD_GRAYSCALE)

        assert color_image is not None, "Color image should not be None"
        assert color_image.size > 0, "Color image should not be empty"

        assert color_image.shape[0] == 250, "Gray image height should be 250"
        assert color_image.shape[1] == 157, "Color image width should be 157"

        # Template matching the color and the output image
        result_color = cv2.matchTemplate(color_image, output_np, cv2.TM_CCOEFF_NORMED)

        assert result_color is not None, "Template matching result should not be None"

        _, max_val_color, _, _ = cv2.minMaxLoc(result_color)

        assert max_val_color > 0.8, "Template matching should have a high correlation"
        assert max_val_color < 1.0, (
            "Template matching should not be perfect (due to noise)"
        )

    def test_on_valid_support_servant_gray(self, tmp_path):
        """Test the creation of support servant image."""
        _, gray_file_path = self.create_support_servant(tmp_path)

        gray_image = cv2.imread(str(gray_file_path), cv2.IMREAD_GRAYSCALE)

        support_img = cv2.imread(str(servant_support_file), cv2.IMREAD_GRAYSCALE)

        # Template matching the support image and the gray image
        result = cv2.matchTemplate(support_img, gray_image, cv2.TM_CCOEFF_NORMED)

        assert result is not None, "Template matching result should not be None"

        _, max_val, _, _ = cv2.minMaxLoc(result)

        assert max_val > 0.8, "Template matching should have a high correlation"
        assert max_val < 1.0, "Template matching should not be perfect (due to noise)"

    def test_on_valid_support_servant_color(self, tmp_path):
        """Test the creation of support servant image."""
        color_file_path, _ = self.create_support_servant(tmp_path)

        color_image = cv2.imread(str(color_file_path), cv2.IMREAD_GRAYSCALE)

        support_img = cv2.imread(str(servant_support_file), cv2.IMREAD_GRAYSCALE)

        # Template matching the support image and the gray image
        result_color = cv2.matchTemplate(support_img, color_image, cv2.TM_CCOEFF_NORMED)

        assert result_color is not None, "Template matching result should not be None"

        _, max_val_color, _, _ = cv2.minMaxLoc(result_color)

        assert max_val_color > 0.8, "Template matching should have a high correlation"
        assert max_val_color < 1.0, (
            "Template matching should not be perfect (due to noise)"
        )
