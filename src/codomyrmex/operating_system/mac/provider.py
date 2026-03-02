"""macOS-specific operating system provider.

Uses native macOS commands (sw_vers, sysctl, diskutil, launchctl,
ifconfig, ps) to gather real system information.
"""

from __future__ import annotations

import os
import platform
import re
import subprocess

from ..base import (
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


def _run(cmd: str, timeout: float = 10.0) -> str:
    """Run a shell command and return stripped stdout."""
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=timeout,
        )
        return result.stdout.strip()
    except Exception:
        return ""


class MacOSProvider(OSProviderBase):
    """macOS implementation of the OS provider."""

    # ── System Info ─────────────────────────────────────────────────

    def get_system_info(self) -> SystemInfo:
        hostname = platform.node()
        arch = platform.machine()
        cpu_count = os.cpu_count() or 1

        # macOS version via sw_vers
        platform_version = _run("sw_vers -productVersion") or platform.mac_ver()[0]

        # Kernel
        kernel_version = _run("uname -r") or platform.release()

        # Total physical memory via sysctl
        mem_raw = _run("sysctl -n hw.memsize")
        try:
            memory_total = int(mem_raw)
        except (ValueError, TypeError):
            memory_total = 0

        # Uptime (seconds since boot)
        boot_raw = _run("sysctl -n kern.boottime")
        uptime = 0.0
        m = re.search(r"sec\s*=\s*(\d+)", boot_raw)
        if m:
            import time
            uptime = time.time() - int(m.group(1))

        return SystemInfo(
            hostname=hostname,
            platform=OSPlatform.MACOS,
            platform_version=platform_version,
            architecture=arch,
            cpu_count=cpu_count,
            memory_total_bytes=memory_total,
            kernel_version=kernel_version,
            uptime_seconds=uptime,
        )

    # ── Processes ───────────────────────────────────────────────────

    def list_processes(self, limit: int = 50) -> list[ProcessInfo]:
        raw = _run(f"ps -eo pid,stat,user,%cpu,rss,comm | head -n {limit + 1}")
        processes: list[ProcessInfo] = []
        for line in raw.splitlines()[1:]:  # skip header
            parts = line.split(None, 5)
            if len(parts) < 6:
                continue
            pid_str, stat, user, cpu, rss, comm = parts
            try:
                pid = int(pid_str)
            except ValueError:
                continue

            status = ProcessStatus.RUNNING
            if stat.startswith("S") or stat.startswith("I"):
                status = ProcessStatus.SLEEPING
            elif stat.startswith("T"):
                status = ProcessStatus.STOPPED
            elif stat.startswith("Z"):
                status = ProcessStatus.ZOMBIE

            processes.append(ProcessInfo(
                pid=pid,
                name=os.path.basename(comm),
                status=status,
                cpu_percent=float(cpu) if cpu.replace(".", "").isdigit() else 0.0,
                memory_bytes=int(rss) * 1024 if rss.isdigit() else 0,
                user=user,
                command=comm,
            ))
        return processes

    # ── Disk Usage ──────────────────────────────────────────────────

    def get_disk_usage(self) -> list[DiskInfo]:
        raw = _run("df -k -T nodevfs,autofs,map")
        disks: list[DiskInfo] = []
        for line in raw.splitlines()[1:]:
            parts = line.split()
            if len(parts) < 9:
                continue
            device = parts[0]
            # df on macOS: Filesystem 512-blocks Used Available Capacity ...
            # With -k: Filesystem 1024-blocks Used Available Capacity ... Mounted
            try:
                total = int(parts[1]) * 1024
                used = int(parts[2]) * 1024
                available = int(parts[3]) * 1024
            except (ValueError, IndexError):
                continue
            pct_str = parts[4].rstrip("%")
            try:
                percent = float(pct_str)
            except ValueError:
                percent = 0.0
            mountpoint = parts[-1]
            disks.append(DiskInfo(
                device=device,
                mountpoint=mountpoint,
                fstype="apfs",  # predominant on modern macOS
                total_bytes=total,
                used_bytes=used,
                free_bytes=available,
                percent_used=percent,
            ))
        return disks

    # ── Services ────────────────────────────────────────────────────

    def get_services(self, pattern: str = "") -> list[ServiceInfo]:
        raw = _run("launchctl list")
        services: list[ServiceInfo] = []
        for line in raw.splitlines()[1:]:
            parts = line.split("\t")
            if len(parts) < 3:
                continue
            pid_str, _status, label = parts
            if pattern and pattern.lower() not in label.lower():
                continue
            try:
                pid = int(pid_str) if pid_str != "-" else None
            except ValueError:
                pid = None
            status = ServiceStatus.RUNNING if pid else ServiceStatus.STOPPED
            services.append(ServiceInfo(
                name=label,
                status=status,
                pid=pid,
                enabled=True,
            ))
        return services

    # ── Network ─────────────────────────────────────────────────────

    def get_network_interfaces(self) -> list[NetworkInfo]:
        raw = _run("ifconfig -a")
        interfaces: list[NetworkInfo] = []
        current_iface = ""
        ip_addr = ""
        mac_addr = ""
        is_up = False

        for line in raw.splitlines():
            # New interface header
            m = re.match(r"^(\w[\w\d]*):.*", line)
            if m:
                if current_iface:
                    interfaces.append(NetworkInfo(
                        interface=current_iface,
                        ip_address=ip_addr,
                        mac_address=mac_addr,
                        is_up=is_up,
                    ))
                current_iface = m.group(1)
                ip_addr = ""
                mac_addr = ""
                is_up = "UP" in line
                continue

            stripped = line.strip()
            if stripped.startswith("inet "):
                parts = stripped.split()
                if len(parts) >= 2:
                    ip_addr = parts[1]
            elif stripped.startswith("ether "):
                parts = stripped.split()
                if len(parts) >= 2:
                    mac_addr = parts[1]

        if current_iface:
            interfaces.append(NetworkInfo(
                interface=current_iface,
                ip_address=ip_addr,
                mac_address=mac_addr,
                is_up=is_up,
            ))

        return interfaces
