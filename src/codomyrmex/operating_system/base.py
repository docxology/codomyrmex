"""
Operating System Module — Base Types and Abstract Provider.

Defines the cross-platform data models and the abstract base class
that each platform-specific provider must implement.
"""

from __future__ import annotations

import os
import subprocess
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any


def run_shell(cmd: str, timeout: float = 10.0) -> str:
    """Run a shell command and return stripped stdout."""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return result.stdout.strip()
    except Exception as _exc:
        return ""


# ── Enums ───────────────────────────────────────────────────────────


class OSPlatform(Enum):
    """Supported operating system platforms."""

    MACOS = "macos"
    WINDOWS = "windows"
    LINUX = "linux"
    UNKNOWN = "unknown"


class ServiceStatus(Enum):
    """Service lifecycle status."""

    RUNNING = "running"
    STOPPED = "stopped"
    UNKNOWN = "unknown"


class ProcessStatus(Enum):
    """Process execution status."""

    RUNNING = "running"
    SLEEPING = "sleeping"
    STOPPED = "stopped"
    ZOMBIE = "zombie"
    UNKNOWN = "unknown"


# ── Data Models ─────────────────────────────────────────────────────


@dataclass
class SystemInfo:
    """System-level information."""

    hostname: str
    platform: OSPlatform
    platform_version: str
    architecture: str
    cpu_count: int
    memory_total_bytes: int
    kernel_version: str
    uptime_seconds: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "hostname": self.hostname,
            "platform": self.platform.value,
            "platform_version": self.platform_version,
            "architecture": self.architecture,
            "cpu_count": self.cpu_count,
            "memory_total_bytes": self.memory_total_bytes,
            "kernel_version": self.kernel_version,
            "uptime_seconds": self.uptime_seconds,
        }


@dataclass
class ProcessInfo:
    """Information about a running process."""

    pid: int
    name: str
    status: ProcessStatus = ProcessStatus.UNKNOWN
    cpu_percent: float = 0.0
    memory_bytes: int = 0
    user: str = ""
    command: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "pid": self.pid,
            "name": self.name,
            "status": self.status.value,
            "cpu_percent": self.cpu_percent,
            "memory_bytes": self.memory_bytes,
            "user": self.user,
            "command": self.command,
        }


@dataclass
class DiskInfo:
    """Disk / volume usage information."""

    device: str
    mountpoint: str
    fstype: str
    total_bytes: int
    used_bytes: int
    free_bytes: int
    percent_used: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "device": self.device,
            "mountpoint": self.mountpoint,
            "fstype": self.fstype,
            "total_bytes": self.total_bytes,
            "used_bytes": self.used_bytes,
            "free_bytes": self.free_bytes,
            "percent_used": self.percent_used,
        }


@dataclass
class ServiceInfo:
    """System service / daemon information."""

    name: str
    status: ServiceStatus = ServiceStatus.UNKNOWN
    pid: int | None = None
    enabled: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "status": self.status.value,
            "pid": self.pid,
            "enabled": self.enabled,
        }


@dataclass
class NetworkInfo:
    """Network interface information."""

    interface: str
    ip_address: str = ""
    mac_address: str = ""
    is_up: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "interface": self.interface,
            "ip_address": self.ip_address,
            "mac_address": self.mac_address,
            "is_up": self.is_up,
        }


@dataclass
class CommandResult:
    """Result of an OS command execution."""

    command: str
    exit_code: int
    stdout: str
    stderr: str
    duration_ms: float

    @property
    def success(self) -> bool:
        return self.exit_code == 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "command": self.command,
            "exit_code": self.exit_code,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "duration_ms": self.duration_ms,
            "success": self.success,
        }


# ── Abstract Provider ───────────────────────────────────────────────


class OSProviderBase(ABC):
    """Abstract base class for platform-specific OS providers.

    Each platform submodule (mac, windows, linux) MUST implement
    a concrete subclass of this provider.
    """

    # ABC: intentional — subclasses supply platform-specific logic

    @abstractmethod
    def get_system_info(self) -> SystemInfo:
        """Return system-level information for this platform."""
        ...  # ABC: intentional

    @abstractmethod
    def list_processes(self, limit: int = 50) -> list[ProcessInfo]:
        """list running processes (up to *limit*)."""
        ...  # ABC: intentional

    @abstractmethod
    def get_disk_usage(self) -> list[DiskInfo]:
        """Return disk / volume usage for all mounted filesystems."""
        ...  # ABC: intentional

    @abstractmethod
    def get_services(self, pattern: str = "") -> list[ServiceInfo]:
        """list system services, optionally filtered by *pattern*."""
        ...  # ABC: intentional

    @abstractmethod
    def get_network_interfaces(self) -> list[NetworkInfo]:
        """Return information about network interfaces."""
        ...  # ABC: intentional

    def execute_command(
        self,
        command: str,
        timeout: float = 30.0,
        cwd: str | None = None,
    ) -> CommandResult:
        """Execute a shell command and return the result.

        This is a concrete method shared by all platforms.
        """
        start = time.time()
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=cwd,
            )
            return CommandResult(
                command=command,
                exit_code=result.returncode,
                stdout=result.stdout,
                stderr=result.stderr,
                duration_ms=(time.time() - start) * 1000,
            )
        except subprocess.TimeoutExpired:
            return CommandResult(
                command=command,
                exit_code=-1,
                stdout="",
                stderr=f"Command timed out after {timeout}s",
                duration_ms=(time.time() - start) * 1000,
            )
        except Exception as exc:
            return CommandResult(
                command=command,
                exit_code=-1,
                stdout="",
                stderr=str(exc),
                duration_ms=(time.time() - start) * 1000,
            )

    def get_environment_variables(self, prefix: str = "") -> dict[str, str]:
        """Return current environment variables, optionally filtered by prefix.

        Concrete method — identical across platforms.
        """
        env = dict(os.environ)
        if prefix:
            env = {k: v for k, v in env.items() if k.startswith(prefix)}
        return env


# ── Exports ─────────────────────────────────────────────────────────

__all__ = [
    "CommandResult",
    "DiskInfo",
    "NetworkInfo",
    "OSPlatform",
    "OSProviderBase",
    "ProcessInfo",
    "ProcessStatus",
    "ServiceInfo",
    "ServiceStatus",
    "SystemInfo",
    "run_shell",
]
