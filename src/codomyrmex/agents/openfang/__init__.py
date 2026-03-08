"""openfang — Agent Operating System integration for codomyrmex.

Wraps the openfang Rust binary (https://github.com/RightNow-AI/openfang)
via subprocess. Tracks upstream via vendor/openfang git submodule.

Install openfang binary:
    curl -fsSL https://openfang.sh/install.sh | sh
Or build from vendor submodule:
    uv run python -c "from codomyrmex.agents.openfang.update import build_and_install; build_and_install()"
"""
import shutil

__version__ = "1.0.0"

HAS_OPENFANG: bool = shutil.which("openfang") is not None

from .config import OpenFangConfig, get_config
from .core import OpenFangRunner, get_openfang_version
from .exceptions import (
    OpenFangBuildError,
    OpenFangConfigError,
    OpenFangError,
    OpenFangNotInstalledError,
    OpenFangTimeoutError,
)
from .hands import HandsManager
from .update import (
    build_and_install,
    build_from_source,
    install_binary,
    update_submodule,
)

# Alias for agent registry compatibility
OpenFangClient = OpenFangRunner

__all__ = [
    "HAS_OPENFANG",
    "HandsManager",
    "OpenFangBuildError",
    "OpenFangClient",
    "OpenFangConfig",
    "OpenFangConfigError",
    "OpenFangError",
    "OpenFangNotInstalledError",
    "OpenFangRunner",
    "OpenFangTimeoutError",
    "build_and_install",
    "build_from_source",
    "get_config",
    "get_openfang_version",
    "install_binary",
    "update_submodule",
]
