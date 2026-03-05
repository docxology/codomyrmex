"""Codomyrmex pai_pm module — PAI Project Manager server wrapper.

Wraps the PAI PM Bun/TypeScript server as a Python module with MCP tools.

Requirements:
  - bun runtime: https://bun.sh
  - Server source: src/codomyrmex/pai_pm/server/server.ts

After install: cd src/codomyrmex/pai_pm/server && bun install
"""

from __future__ import annotations

import shutil

from codomyrmex.pai_pm.config import PaiPmConfig, get_config
from codomyrmex.pai_pm.exceptions import (
    PaiPmConnectionError,
    PaiPmError,
    PaiPmNotInstalledError,
    PaiPmServerError,
    PaiPmTimeoutError,
)
from codomyrmex.pai_pm.server_manager import PaiPmServerManager, get_bun_version

__version__ = "1.0.0"

# Feature flag — True when bun binary is available in PATH
HAS_BUN: bool = shutil.which("bun") is not None

__all__ = [
    "PaiPmConfig",
    "PaiPmError",
    "PaiPmNotInstalledError",
    "PaiPmServerError",
    "PaiPmTimeoutError",
    "PaiPmConnectionError",
    "PaiPmServerManager",
    "HAS_BUN",
    "get_bun_version",
    "get_config",
]
