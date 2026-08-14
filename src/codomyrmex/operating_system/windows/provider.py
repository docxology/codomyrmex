"""Windows-specific operating system provider.

Uses native Windows commands (systeminfo, wmic, tasklist, sc,
ipconfig, powershell) to gather real system information.
"""

from __future__ import annotations

import csv
import ctypes
import os
import platform
import re
import subprocess

from codomyrmex.operating_system.base import (
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


def _run(cmd: str, timeout: float = 15.0) -> str:
    """Run a shell command and return stripped stdout."""
    try:
        # On Windows, no need for shell=True with explicit executables,
        # but we keep shell=True for compound commands.
        result = subprocess.run(
            cmd,
            shell=True,  # nosec B602
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return result.stdout.strip()
    except Exception as _exc:
        return ""


def _powershell(script: str, timeout: float = 15.0) -> str:
    """Run a PowerShell one-liner."""
    return _run(f'powershell -NoProfile -Command "{script}"', timeout=timeout)


def _total_physical_memory() -> int:
    """Return installed physical memory through the native Windows API."""

    class MemoryStatusEx(ctypes.Structure):
        _fields_ = [
            ("dwLength", ctypes.c_ulong),
            ("dwMemoryLoad", ctypes.c_ulong),
            ("ullTotalPhys", ctypes.c_ulonglong),
            ("ullAvailPhys", ctypes.c_ulonglong),
            ("ullTotalPageFile", ctypes.c_ulonglong),
            ("ullAvailPageFile", ctypes.c_ulonglong),
            ("ullTotalVirtual", ctypes.c_ulonglong),
            ("ullAvailVirtual", ctypes.c_ulonglong),
            ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
        ]

    windll = getattr(ctypes, "windll", None)
    if windll is None:
        return 0

    status = MemoryStatusEx()
    status.dwLength = ctypes.sizeof(status)
    try:
        if windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
            return int(status.ullTotalPhys)
    except (AttributeError, OSError):
        pass
    return 0


class WindowsProvider(OSProviderBase):
    """Windows implementation of the OS provider."""

    # ── System Info ─────────────────────────────────────────────────

    def get_system_info(self) -> SystemInfo:
        hostname = platform.node()
        arch = platform.machine()
        cpu_count = os.cpu_count() or 1

        platform_version = platform.version()
        kernel_version = platform.release()

        # WMIC is no longer installed by default on current Windows releases.
        # GlobalMemoryStatusEx is available on every supported Windows version.
        memory_total = _total_physical_memory()

        # Uptime via powershell
        uptime_raw = _powershell(
            "(Get-Date) - (gcim Win32_OperatingSystem).LastBootUpTime | "
            "Select-Object -ExpandProperty TotalSeconds"
        )
        try:
            uptime = float(uptime_raw)
        except (ValueError, TypeError):
            uptime = 0.0

        return SystemInfo(
            hostname=hostname,
            platform=OSPlatform.WINDOWS,
            platform_version=platform_version,
            architecture=arch,
            cpu_count=cpu_count,
            memory_total_bytes=memory_total,
            kernel_version=kernel_version,
            uptime_seconds=uptime,
        )

    # ── Processes ───────────────────────────────────────────────────

    def list_processes(self, limit: int = 50) -> list[ProcessInfo]:
        if limit <= 0:
            return []

        raw = _run("tasklist /FO CSV /NH")
        processes: list[ProcessInfo] = []
        for row in csv.reader(raw.splitlines()):
            if len(row) < 5:
                continue
            try:
                pid = int(row[1])
            except ValueError:
                continue
            if pid <= 0:
                # Windows exposes "System Idle Process" as PID 0. The shared
                # ProcessInfo contract represents schedulable OS processes.
                continue
            name = row[0]
            memory_kib = re.sub(r"[^\d]", "", row[4])
            mem = int(memory_kib) * 1024 if memory_kib else 0
            processes.append(
                ProcessInfo(
                    pid=pid,
                    name=name,
                    status=ProcessStatus.RUNNING,
                    cpu_percent=0.0,
                    memory_bytes=mem,
                    user="",
                    command=name,
                )
            )
            if len(processes) >= limit:
                break
        return processes

    # ── Disk Usage ──────────────────────────────────────────────────

    def get_disk_usage(self) -> list[DiskInfo]:
        raw = _powershell(
            "Get-PSDrive -PSProvider FileSystem | "
            "Select-Object Name,Used,Free "
            "| Format-Table -HideTableHeaders -AutoSize"
        )
        disks: list[DiskInfo] = []
        for line in raw.splitlines():
            parts = line.split()
            if len(parts) < 3:
                continue
            drive_letter = parts[0]
            try:
                used = int(parts[1])
                free = int(parts[2])
            except ValueError:
                continue
            total = used + free
            percent = (used / total * 100) if total > 0 else 0.0
            disks.append(
                DiskInfo(
                    device=f"{drive_letter}:",
                    mountpoint=f"{drive_letter}:\\",
                    fstype="NTFS",
                    total_bytes=total,
                    used_bytes=used,
                    free_bytes=free,
                    percent_used=round(percent, 1),
                )
            )
        return disks

    # ── Services ────────────────────────────────────────────────────

    def get_services(self, pattern: str = "") -> list[ServiceInfo]:
        filter_clause = (
            f"| Where-Object {{$_.Name -like '*{pattern}*'}}" if pattern else ""
        )
        raw = _powershell(
            f"Get-Service {filter_clause} | "
            "Select-Object Name,Status "
            "| Format-Table -HideTableHeaders -AutoSize"
        )
        services: list[ServiceInfo] = []
        for line in raw.splitlines():
            parts = line.split(None, 1)
            if len(parts) < 2:
                continue
            name = parts[0]
            status_str = parts[1].strip().lower()
            status = (
                ServiceStatus.RUNNING
                if status_str == "running"
                else ServiceStatus.STOPPED
            )
            services.append(
                ServiceInfo(
                    name=name,
                    status=status,
                    pid=None,
                    enabled=status == ServiceStatus.RUNNING,
                )
            )
        return services

    # ── Network ─────────────────────────────────────────────────────

    def get_network_interfaces(self) -> list[NetworkInfo]:
        raw = _powershell(
            "Get-NetAdapter | Select-Object Name,MacAddress,Status "
            "| Format-Table -HideTableHeaders -AutoSize"
        )
        interfaces: list[NetworkInfo] = []

        # Build name -> IP mapping
        ip_raw = _powershell(
            "Get-NetIPAddress -AddressFamily IPv4 "
            "| Select-Object InterfaceAlias,IPAddress "
            "| Format-Table -HideTableHeaders -AutoSize"
        )
        ip_map: dict[str, str] = {}
        for line in ip_raw.splitlines():
            parts = line.rsplit(None, 1)
            if len(parts) == 2:
                ip_map[parts[0].strip()] = parts[1].strip()

        for line in raw.splitlines():
            parts = line.rsplit(None, 2)
            if len(parts) < 3:
                continue
            name = parts[0].strip()
            mac = parts[1].strip()
            status_str = parts[2].strip().lower()
            interfaces.append(
                NetworkInfo(
                    interface=name,
                    ip_address=ip_map.get(name, ""),
                    mac_address=mac,
                    is_up=status_str == "up",
                )
            )

        return interfaces
