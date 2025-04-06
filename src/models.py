import re
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path

from enums import SupportKind

# Sanitize the 'name' to ensure it's a valid Windows directory name
INVALID_CHARS_PATTERN = r'[<>:"/\\|?*\x00-\x1f]|\.$'


@dataclass
class SupportFolder:
    """Class representing a support folder.
    Attributes:
        path (Path): The path to the folder.
        name (str): The name of the folder.
        idx (int): The index of the folder
        kind (SupportKind): The type of support.
    """

    path: Path
    name: str
    idx: int
    kind: SupportKind


def _preprocess_name(input_str) -> str:
    """Removes accents from a string using unicode normalization.

    Args:
        input_str: The string to process.

    Returns:
        The string with accents removed.
    """
    nfkd_form = unicodedata.normalize("NFKD", input_str)
    only_ascii = "".join([c for c in nfkd_form if not unicodedata.combining(c)])
    return only_ascii


def _cleanup_name(name: str) -> str:
    """Cleans up the name by removing invalid characters and normalizing it.

    Args:
        name: The name to clean up.

    Returns:
        str: The cleaned-up name.
    """
    sanitized_name = re.sub(INVALID_CHARS_PATTERN, " ", name)
    sanitized_name = sanitized_name.strip()
    sanitized_name = _preprocess_name(sanitized_name)
    return sanitized_name


@dataclass
class Assets:
    """
    Class representing an asset.

    After downloading the asset, update the file_path attribute.

    Attributes:
        url (str): The URL of the asset.
        file_path (Path | None): The file path of the asset.
    """

    url: str
    file_path: Path | None = None

    def update_file_path(self, file_path: Path):
        """
        Update the file path of the asset.
        This method is called after the asset has been downloaded.
        It checks if the file exists and if its size is greater than 100 bytes.
        If the file does not exist or its size is less than or equal to 100 bytes,

        Args:
            file_path (Path): The new file path.
        """
        if not file_path.exists():
            return

        file_size = file_path.stat().st_size

        if file_size <= 100:
            return

        self.file_path = file_path


@dataclass
class ServantData:
    idx: int
    name: str
    class_name: str
    rarity: int
    faces: list[Assets] = field(default_factory=list)

    @property
    def is_empty(self):
        """
        Check if the servant data is empty.

        Returns:
            bool: True if the servant data is empty, False otherwise.
        """
        return len(self.faces) == 0

    @property
    def sanitized_name(self):
        """
        Get the sanitized name of the servant.

        Returns:
            str: The sanitized name of the servant.
        """
        return _cleanup_name(self.name)


@dataclass
class CraftEssenceData:
    idx: int
    name: str
    rarity: int
    faces: Assets | None = None

    @property
    def is_empty(self):
        """
        Check if the craft essence data is empty.

        Returns:
            bool: True if the craft essence data is empty, False otherwise.
        """
        return self.faces is None

    @property
    def sanitized_name(self):
        """
        Get the sanitized name of the craft essence.

        Returns:
            str: The sanitized name of the craft essence.
        """
        return _cleanup_name(self.name)
