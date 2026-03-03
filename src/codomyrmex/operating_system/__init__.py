"""
Codomyrmex Operating System Module.

Cross-platform operating system abstraction with generic methods and
platform-specific submodules for macOS, Linux, and Windows.

The module auto-detects the current platform and dispatches calls to
the correct provider. Generic functions work identically on every OS.

Integration:
- Uses ``subprocess`` + native OS commands (zero external dependencies).
- Providers are lazily loaded via ``get_provider()`` and cached.

Available functions (generic / cross-platform):
- detect_platform
- get_provider
- get_system_info
- list_processes
- get_disk_usage
- get_services
- get_network_interfaces
- execute_command
- get_environment_variables
"""

from .base import (
    CommandResult,
    DiskInfo,
    NetworkInfo,
    OSPlatform,
    OSProviderBase,
    ProcessInfo,
    ProcessStatus,
    ServiceInfo,
    ServiceStatus,
    SystemInfo,
)
from .detector import (
    detect_platform,
    execute_command,
    get_disk_usage,
    get_environment_variables,
    get_network_interfaces,
    get_provider,
    get_services,
    get_system_info,
    list_processes,
)

# Shared schemas for cross-module interop
try:
    from codomyrmex.validation.schemas import Result, ResultStatus
except ImportError:
    Result = None
    ResultStatus = None


def cli_commands():
    """Return CLI commands for the operating_system module."""
    return {
        "info": {
            "help": "Display system information for the current platform",
            "handler": lambda **kwargs: print(get_system_info()),
        },
        "platform": {
            "help": "Show the detected platform",
            "handler": lambda **kwargs: print(f"Platform: {detect_platform().value}"),
        },
        "disk": {
            "help": "Show disk usage",
            "handler": lambda **kwargs: print(
                "\n".join(str(d) for d in get_disk_usage())
            ),
        },
        "processes": {
            "help": "List running processes",
            "handler": lambda **kwargs: print(
                "\n".join(f"[{p.pid}] {p.name}" for p in list_processes(limit=20))
            ),
        },
    }


__all__ = [
    # Enums
    "OSPlatform",
    "ServiceStatus",
    "ProcessStatus",
    # Data models
    "SystemInfo",
    "ProcessInfo",
    "DiskInfo",
    "ServiceInfo",
    "NetworkInfo",
    "CommandResult",
    # Base
    "OSProviderBase",
    # Generic API
    "detect_platform",
    "get_provider",
    "get_system_info",
    "list_processes",
    "get_disk_usage",
    "get_services",
    "get_network_interfaces",
    "execute_command",
    "get_environment_variables",
    # CLI
    "cli_commands",
]

__version__ = "0.1.0"
