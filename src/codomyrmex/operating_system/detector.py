"""
Operating System Module — Platform Detection and Dispatch.

Detects the current operating system and provides a convenience
API that delegates to the appropriate platform-specific provider.
"""

from __future__ import annotations

import platform as _platform
from functools import lru_cache

from .base import (
    CommandResult,
    DiskInfo,
    NetworkInfo,
    OSPlatform,
    OSProviderBase,
    ProcessInfo,
    ServiceInfo,
    SystemInfo,
)

# ── Detection ───────────────────────────────────────────────────────


def detect_platform() -> OSPlatform:
    """Detect the current operating system platform.

    Returns:
        An ``OSPlatform`` enum member (``MACOS``, ``LINUX``, ``WINDOWS``,
        or ``UNKNOWN``).
    """
    system = _platform.system().lower()
    mapping = {
        "darwin": OSPlatform.MACOS,
        "linux": OSPlatform.LINUX,
        "windows": OSPlatform.WINDOWS,
    }
    return mapping.get(system, OSPlatform.UNKNOWN)


@lru_cache(maxsize=1)
def get_provider() -> OSProviderBase:
    """Return the platform-specific provider for the current OS.

    The provider is cached after first invocation.

    Raises:
        RuntimeError: If the current platform is unsupported.
    """
    current = detect_platform()

    if current == OSPlatform.MACOS:
        from .mac.provider import MacOSProvider

        return MacOSProvider()

    if current == OSPlatform.LINUX:
        from .linux.provider import LinuxProvider

        return LinuxProvider()

    if current == OSPlatform.WINDOWS:
        from .windows.provider import WindowsProvider

        return WindowsProvider()

    raise RuntimeError(
        f"Unsupported platform: {_platform.system()!r}. "
        "Supported platforms: macOS, Linux, Windows."
    )


# ── Generic Dispatch Functions ──────────────────────────────────────


def get_system_info() -> SystemInfo:
    """Return system information for the current platform."""
    return get_provider().get_system_info()


def list_processes(limit: int = 50) -> list[ProcessInfo]:
    """List running processes on the current platform."""
    return get_provider().list_processes(limit=limit)


def get_disk_usage() -> list[DiskInfo]:
    """Return disk usage for all mounted filesystems."""
    return get_provider().get_disk_usage()


def get_services(pattern: str = "") -> list[ServiceInfo]:
    """List system services, optionally filtered by *pattern*."""
    return get_provider().get_services(pattern=pattern)


def get_network_interfaces() -> list[NetworkInfo]:
    """Return network interface information."""
    return get_provider().get_network_interfaces()


def execute_command(
    command: str,
    timeout: float = 30.0,
    cwd: str | None = None,
) -> CommandResult:
    """Execute a shell command on the current platform."""
    return get_provider().execute_command(command, timeout=timeout, cwd=cwd)


def get_environment_variables(prefix: str = "") -> dict[str, str]:
    """Return environment variables, optionally filtered by prefix."""
    return get_provider().get_environment_variables(prefix=prefix)


# ── Exports ─────────────────────────────────────────────────────────

__all__ = [
    "detect_platform",
    "execute_command",
    "get_disk_usage",
    "get_environment_variables",
    "get_network_interfaces",
    "get_provider",
    "get_services",
    "get_system_info",
    "list_processes",
]
