"""Codomyrmex aider module -- AI pair programming via the aider CLI.

Install aider: uv tool install aider-chat
Install module dep: uv sync --extra aider
"""

from __future__ import annotations

import shutil

from codomyrmex.aider.config import AiderConfig, get_config
from codomyrmex.aider.core import AiderRunner, get_aider_version
from codomyrmex.aider.exceptions import (
    AiderAPIKeyError,
    AiderError,
    AiderNotInstalledError,
    AiderTimeoutError,
)

__version__ = "1.0.0"

# Feature flag -- True when aider binary is available in PATH
HAS_AIDER: bool = shutil.which("aider") is not None

__all__ = [
    "HAS_AIDER",
    "AiderAPIKeyError",
    "AiderConfig",
    "AiderError",
    "AiderNotInstalledError",
    "AiderRunner",
    "AiderTimeoutError",
    "get_aider_version",
    "get_config",
]
