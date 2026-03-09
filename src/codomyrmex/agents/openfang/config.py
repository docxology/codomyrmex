"""openfang configuration dataclass — all values from environment variables."""

import os
from dataclasses import dataclass, field
from pathlib import Path


def _default_vendor_dir() -> str:
    """Compute vendor dir relative to this module's location."""
    return str(Path(__file__).parent / "vendor" / "openfang")


@dataclass
class OpenFangConfig:
    """Configuration for the openfang integration.

    All fields default to environment variables with sensible fallbacks.
    """

    command: str = field(
        default_factory=lambda: os.getenv("OPENFANG_COMMAND", "openfang")
    )
    timeout: int = field(
        default_factory=lambda: int(os.getenv("OPENFANG_TIMEOUT", "120"))
    )
    gateway_url: str = field(
        default_factory=lambda: os.getenv("OPENFANG_GATEWAY_URL", "ws://localhost:3000")
    )
    vendor_dir: str = field(default_factory=_default_vendor_dir)
    install_dir: str = field(
        default_factory=lambda: os.getenv("OPENFANG_INSTALL_DIR", "/usr/local/bin")
    )

    @property
    def vendor_path(self) -> Path:
        """Return vendor_dir as a Path object."""
        return Path(self.vendor_dir)

    @property
    def is_submodule_initialized(self) -> bool:
        """True if vendor/openfang git submodule has been initialized."""
        return (self.vendor_path / "Cargo.toml").exists()

    @property
    def cargo_binary(self) -> Path:
        """Path to compiled release binary inside vendor submodule."""
        return self.vendor_path / "target" / "release" / "openfang"


def get_config() -> OpenFangConfig:
    """Return a new OpenFangConfig instance from current environment."""
    return OpenFangConfig()
