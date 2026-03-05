"""Codomyrmex agents/google_workspace module -- subprocess wrapper for gws CLI.

Install gws: npm install -g @googleworkspace/cli
Configure:   gws auth setup && gws auth login --account your@workspace.com
"""

from __future__ import annotations

import shutil

from codomyrmex.agents.google_workspace.config import GWSConfig, get_config
from codomyrmex.agents.google_workspace.core import (
    GoogleWorkspaceRunner,
    get_gws_version,
)
from codomyrmex.agents.google_workspace.exceptions import (
    GWSAuthError,
    GWSCommandError,
    GWSError,
    GWSNotInstalledError,
    GWSTimeoutError,
)

HAS_GWS: bool = shutil.which("gws") is not None

__all__ = [
    "HAS_GWS",
    "GWSAuthError",
    "GWSCommandError",
    "GWSConfig",
    "GWSError",
    "GWSNotInstalledError",
    "GWSTimeoutError",
    "GoogleWorkspaceRunner",
    "get_config",
    "get_gws_version",
]
