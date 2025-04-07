import re
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import unquote, urlparse

from enums import SupportKind

# Sanitize the 'name' to ensure it's a valid Windows directory name
INVALID_CHARS_PATTERN = r'[<>:"/\\|?*\x00-\x1f]|\.$'

type CraftEssenceDataIndexed = dict[int, CraftEssenceData]
type ServantDataIndexed = dict[int, ServantData]


@dataclass
class SupportFolder:
    """Class representing a support folder.
    Attributes:
        path (Path): The path to the folder.
        idx (int): The index of the folder
        kind (SupportKind): The type of support.
        name (str | None): The name of the folder.
            if None, the name will be set later
    """

    path: Path
    idx: int
    kind: SupportKind
    name: str | None = None

    def __post_init__(self):
        if isinstance(self.kind, str):
            try:
                self.kind = SupportKind(self.kind)
            except ValueError as err:
                raise ValueError(f"Invalid support kind: {self.kind}") from err


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
        key (str): The key of the asset.
        url (str): The URL of the asset.
    """

    key: str
    url: str

    @property
    def url_file_name(self) -> str:
        """
        Get the file name from the URL.

        Returns:
            str: The file name extracted from the URL.
        """
        path = urlparse(self.url).path
        return unquote(path.split("/")[-1])


@dataclass
class BaseData:
    idx: int
    name: str
    rarity: int
    assets: list[Assets] = field(default_factory=list)

    def __post_init__(self):
        """
        Post-initialization processing to ensure the name is sanitized.
        """
        self.name = _cleanup_name(self.name)

    @property
    def sanitized_name(self):
        """
        Get the sanitized name of the craft essence.

        Returns:
            str: The sanitized name of the craft essence.
        """
        return _cleanup_name(self.name)

    @property
    def is_empty(self):
        """
        Check if the data is empty.

        Returns:
            bool: True if the data is empty, False otherwise.
        """
        return len(self.assets) == 0


@dataclass
class ServantData(BaseData):
    class_name: str = ""


@dataclass
class CraftEssenceData(BaseData):
    pass
