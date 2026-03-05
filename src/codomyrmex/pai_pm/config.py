"""Configuration for the pai_pm module."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class PaiPmConfig:
    """Configuration for PAI Project Manager server operations."""

    port: int = field(default_factory=lambda: int(os.getenv("PAI_PM_PORT", "8889")))
    host: str = field(default_factory=lambda: os.getenv("PAI_PM_HOST", "127.0.0.1"))
    startup_timeout: int = field(
        default_factory=lambda: int(os.getenv("PAI_PM_STARTUP_TIMEOUT", "10"))
    )
    request_timeout: int = field(
        default_factory=lambda: int(os.getenv("PAI_PM_REQUEST_TIMEOUT", "30"))
    )
    server_script: str = field(
        default_factory=lambda: os.getenv(
            "PAI_PM_SERVER_SCRIPT",
            str(Path(__file__).parent / "server" / "server.ts"),
        )
    )


def get_config() -> PaiPmConfig:
    """Return a PaiPmConfig populated from environment variables."""
    return PaiPmConfig()
