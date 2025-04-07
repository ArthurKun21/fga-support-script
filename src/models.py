import re
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path

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
        return self.url.split("/")[-1]


@dataclass
class BaseData:
    idx: int
    name: str
    rarity: int
    assets: list[Assets] = field(default_factory=list)

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

    @classmethod
    def create(
        cls,
        idx: int,
        name: str,
        class_name: str,
        rarity: int,
        assets: list[Assets] | None = None,
    ) -> "ServantData":
        """
        Create a new instance of ServantData.

        Args:
            idx (int): The index of the servant.
            name (str): The name of the servant.
            class_name (str): The class of the servant.
            rarity (int): The rarity of the servant.
            assets (list[Assets] | None): The list of assets for the servant.

        Returns:
            ServantData: A new instance of ServantData.
        """
        if assets is None:
            assets = []

        name = _cleanup_name(name)

        return cls(
            class_name=class_name,
            idx=idx,
            name=name,
            rarity=rarity,
            assets=assets,
        )


@dataclass
class CraftEssenceData(BaseData):
    @property
    def asset(self) -> Assets | None:
        """
        Get the first asset of the craft essence.

        Returns:
            Assets | None: The first asset of the craft essence or None
            if no assets are available.
        """
        if len(self.assets) > 0:
            return self.assets[0]
        return None
