"""Windows-specific operating system provider.

Uses native Windows commands (systeminfo, wmic, tasklist, sc,
ipconfig, powershell) to gather real system information.
"""

from __future__ import annotations

import os
import platform
import re
import subprocess

from src.codomyrmex.operating_system.base import (
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
            cmd, shell=True, capture_output=True, text=True, timeout=timeout,
        )
        return result.stdout.strip()
    except Exception:
        return ""


def _powershell(script: str, timeout: float = 15.0) -> str:
    """Run a PowerShell one-liner."""
    return _run(f'powershell -NoProfile -Command "{script}"', timeout=timeout)


class WindowsProvider(OSProviderBase):
    """Windows implementation of the OS provider."""

    # ── System Info ─────────────────────────────────────────────────

    def get_system_info(self) -> SystemInfo:
        hostname = platform.node()
        arch = platform.machine()
        cpu_count = os.cpu_count() or 1

        platform_version = platform.version()
        kernel_version = platform.release()

        # Total physical memory via wmic
        mem_raw = _run("wmic ComputerSystem get TotalPhysicalMemory /Format:Value")
        try:
            m = re.search(r"TotalPhysicalMemory=(\d+)", mem_raw)
            memory_total = int(m.group(1)) if m else 0
        except (ValueError, AttributeError):
            memory_total = 0

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
        raw = _powershell(
            f"Get-Process | Select-Object -First {limit} "
            "Id,ProcessName,@{{N='CPU';E={{$_.CPU}}}},@{{N='WS';E={{$_.WorkingSet64}}}},@{{N='User';E={{'N/A'}}}} "
            "| Format-Table -HideTableHeaders -AutoSize"
        )
        processes: list[ProcessInfo] = []
        for line in raw.splitlines():
            parts = line.split(None, 4)
            if len(parts) < 4:
                continue
            try:
                pid = int(parts[0])
            except ValueError:
                continue
            name = parts[1]
            try:
                cpu = float(parts[2])
            except ValueError:
                cpu = 0.0
            try:
                mem = int(parts[3])
            except ValueError:
                mem = 0
            processes.append(ProcessInfo(
                pid=pid,
                name=name,
                status=ProcessStatus.RUNNING,
                cpu_percent=cpu,
                memory_bytes=mem,
                user=parts[4].strip() if len(parts) > 4 else "",
                command=name,
            ))
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
            disks.append(DiskInfo(
                device=f"{drive_letter}:",
                mountpoint=f"{drive_letter}:\\",
                fstype="NTFS",
                total_bytes=total,
                used_bytes=used,
                free_bytes=free,
                percent_used=round(percent, 1),
            ))
        return disks

    # ── Services ────────────────────────────────────────────────────

    def get_services(self, pattern: str = "") -> list[ServiceInfo]:
        filter_clause = f"| Where-Object {{$_.Name -like '*{pattern}*'}}" if pattern else ""
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
            status = ServiceStatus.RUNNING if status_str == "running" else ServiceStatus.STOPPED
            services.append(ServiceInfo(
                name=name,
                status=status,
                pid=None,
                enabled=status == ServiceStatus.RUNNING,
            ))
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
            interfaces.append(NetworkInfo(
                interface=name,
                ip_address=ip_map.get(name, ""),
                mac_address=mac,
                is_up=status_str == "up",
            ))

        return interfaces
