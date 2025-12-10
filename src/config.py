"""
Centralized configuration for the FGA Data Script.

This module provides a unified configuration system that:
- Maps SupportKind to related paths, URLs, and processors
- Reduces duplication across the codebase
- Makes it easier to add new support types in the future
"""

import os
from dataclasses import dataclass, field
from pathlib import Path

from enums import SupportKind

# Root directory
ROOT = Path(__file__).parent.parent


@dataclass(frozen=True)
class DirectoryConfig:
    """Configuration for directory paths."""

    root: Path = ROOT
    logs_dir: Path = field(default_factory=lambda: ROOT / "logs")
    tmp_dir: Path = field(default_factory=lambda: ROOT / "tmp")
    output_dir: Path = field(default_factory=lambda: ROOT / "output")
    data_dir: Path = field(default_factory=lambda: ROOT / "data")
    repo_dir: Path = field(default_factory=lambda: ROOT / "fga-support")

    def ensure_directories(self) -> None:
        """Create all necessary directories."""
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self.tmp_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.data_dir.mkdir(parents=True, exist_ok=True)


@dataclass(frozen=True)
class SupportKindPaths:
    """Path configuration for a specific SupportKind."""

    kind: SupportKind
    base_dir: Path

    @property
    def name(self) -> str:
        return self.kind.value

    @property
    def temp_dir(self) -> Path:
        return self.base_dir / "tmp" / self.name

    @property
    def output_dir(self) -> Path:
        return self.base_dir / "output" / self.name

    @property
    def output_color_dir(self) -> Path:
        return self.base_dir / "output" / f"{self.name}-color"

    @property
    def repo_dir(self) -> Path:
        return self.base_dir / "fga-support" / self.name

    @property
    def repo_color_dir(self) -> Path:
        return self.base_dir / "fga-support" / f"{self.name}-color"

    @property
    def remote_data_file(self) -> Path:
        return self.base_dir / "data" / f"{self.name}.json"

    @property
    def local_data_file(self) -> Path:
        return self.base_dir / "data" / f"local-{self.name}.json"

    def ensure_directories(self) -> None:
        """Create all directories for this support kind."""
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.output_color_dir.mkdir(parents=True, exist_ok=True)


@dataclass
class SupportKindConfig:
    """
    Complete configuration for a SupportKind.

    This class encapsulates all the configuration needed to process
    a specific support type (Servant or Craft Essence).
    """

    kind: SupportKind
    paths: SupportKindPaths
    url_env_var: str
    output_image_filename: str
    display_name: str

    @property
    def url(self) -> str | None:
        """Get the URL from environment variable."""
        return os.getenv(self.url_env_var)

    def has_valid_url(self) -> bool:
        """Check if a valid URL is configured."""
        return self.url is not None and len(self.url) > 0


class AppConfig:
    """
    Main application configuration.

    Provides access to all configuration in a centralized manner.
    """

    def __init__(self, root: Path = ROOT):
        self.root = root
        self.directories = DirectoryConfig(root=root)

        # Create support kind configurations
        self._support_configs: dict[SupportKind, SupportKindConfig] = {}
        self._init_support_configs()

    def _init_support_configs(self) -> None:
        """Initialize configurations for all support kinds."""
        servant_paths = SupportKindPaths(
            kind=SupportKind.SERVANT,
            base_dir=self.root,
        )
        self._support_configs[SupportKind.SERVANT] = SupportKindConfig(
            kind=SupportKind.SERVANT,
            paths=servant_paths,
            url_env_var="SERVANT_URL",
            output_image_filename="support.png",
            display_name="Servant",
        )

        ce_paths = SupportKindPaths(
            kind=SupportKind.CRAFT_ESSENCE,
            base_dir=self.root,
        )
        self._support_configs[SupportKind.CRAFT_ESSENCE] = SupportKindConfig(
            kind=SupportKind.CRAFT_ESSENCE,
            paths=ce_paths,
            url_env_var="CE_URL",
            output_image_filename="ce.png",
            display_name="Craft Essence",
        )

    def get_support_config(self, kind: SupportKind) -> SupportKindConfig:
        """Get configuration for a specific support kind."""
        return self._support_configs[kind]

    def get_all_support_configs(self) -> list[SupportKindConfig]:
        """Get all support kind configurations."""
        return list(self._support_configs.values())

    @property
    def log_file(self) -> Path:
        """Get the log file path."""
        return self.directories.logs_dir / "app.log"

    @property
    def repo_path(self) -> Path:
        """Get the repository path."""
        return self.directories.repo_dir

    def ensure_all_directories(self) -> None:
        """Create all necessary directories."""
        self.directories.ensure_directories()
        for config in self._support_configs.values():
            config.paths.ensure_directories()


# Global configuration instance
# This can be imported and used throughout the application
app_config = AppConfig()

# Ensure directories exist on import
app_config.ensure_all_directories()
