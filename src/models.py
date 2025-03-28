import re
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class SupportFolder:
    """Class representing a support folder.
    Attributes:
        path (Path): The path to the folder.
        name (str): The name of the folder.
        idx (int): The index of the folder, default is 0.
            This is extracted from the folder name if it contains a number.
    """

    path: Path
    name: str
    idx: int = 0

    def __post_init__(self):
        directory_name = self.path.name

        match = re.search(r"(\d+)", directory_name)
        if match:
            self.idx = int(match.group(1))


@dataclass
class ServantData:
    idx: int
    name: str
    class_name: str
    rarity: int
    faces: list[str] = field(default_factory=list)

    @property
    def is_empty(self):
        """
        Check if the servant data is empty.

        Returns:
            bool: True if the servant data is empty, False otherwise.
        """
        return len(self.faces) == 0


@dataclass
class CraftEssenceData:
    idx: int
    name: str
    faces: str | None = None

    @property
    def is_empty(self):
        """
        Check if the craft essence data is empty.

        Returns:
            bool: True if the craft essence data is empty, False otherwise.
        """
        return self.faces is None
