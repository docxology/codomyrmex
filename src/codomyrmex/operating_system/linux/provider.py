"""Linux-specific operating system provider.

Uses native Linux commands (uname, lsb_release, /proc, df,
systemctl, ip, ps) to gather real system information.
"""

from __future__ import annotations

import os
import platform
import re

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
    run_shell,
)


class LinuxProvider(OSProviderBase):
    """Linux implementation of the OS provider."""

    # ── System Info ─────────────────────────────────────────────────

    def get_system_info(self) -> SystemInfo:
        hostname = platform.node()
        arch = platform.machine()
        cpu_count = os.cpu_count() or 1

        # Distribution version
        platform_version = ""
        try:
            with open("/etc/os-release") as f:
                for line in f:
                    if line.startswith("PRETTY_NAME="):
                        platform_version = line.strip().split("=", 1)[1].strip('"')
                        break
        except FileNotFoundError:
            pass
        if not platform_version:
            platform_version = run_shell("uname -r")

        kernel_version = run_shell("uname -r") or platform.release()

        # Memory from /proc/meminfo
        memory_total = 0
        try:
            with open("/proc/meminfo") as f:
                for line in f:
                    if line.startswith("MemTotal:"):
                        parts = line.split()
                        if len(parts) >= 2:
                            memory_total = int(parts[1]) * 1024
                        break
        except (FileNotFoundError, ValueError, TypeError):
            memory_total = 0

        # Uptime from /proc/uptime
        uptime = 0.0
        try:
            with open("/proc/uptime") as f:
                content = f.read().strip()
                if content:
                    uptime = float(content.split()[0])
        except (FileNotFoundError, ValueError, TypeError):
            uptime = 0.0

        return SystemInfo(
            hostname=hostname,
            platform=OSPlatform.LINUX,
            platform_version=platform_version,
            architecture=arch,
            cpu_count=cpu_count,
            memory_total_bytes=memory_total,
            kernel_version=kernel_version,
            uptime_seconds=uptime,
        )

    # ── Processes ───────────────────────────────────────────────────

    def list_processes(self, limit: int = 50) -> list[ProcessInfo]:
        import subprocess

        # Avoid shell pipelines: use subprocess.run directly for pipeline simulation
        try:
            ps_result = subprocess.run(
                ["ps", "-eo", "pid,stat,user,%cpu,rss,comm", "--no-headers"],
                capture_output=True,
                text=True,
                shell=False,
            )
            raw = ps_result.stdout
        except FileNotFoundError:
            raw = ""

        processes: list[ProcessInfo] = []
        lines = raw.splitlines()[:limit]
        for line in lines:
            parts = line.split(None, 5)
            if len(parts) < 6:
                continue
            pid_str, stat, user, cpu, rss, comm = parts
            try:
                pid = int(pid_str)
            except ValueError:
                continue

            status = ProcessStatus.RUNNING
            if stat.startswith("S"):
                status = ProcessStatus.SLEEPING
            elif stat.startswith("T"):
                status = ProcessStatus.STOPPED
            elif stat.startswith("Z"):
                status = ProcessStatus.ZOMBIE

            processes.append(
                ProcessInfo(
                    pid=pid,
                    name=os.path.basename(comm),
                    status=status,
                    cpu_percent=float(cpu) if cpu.replace(".", "").isdigit() else 0.0,
                    memory_bytes=int(rss) * 1024 if rss.isdigit() else 0,
                    user=user,
                    command=comm,
                )
            )
        return processes

    # ── Disk Usage ──────────────────────────────────────────────────

    def get_disk_usage(self) -> list[DiskInfo]:
        import subprocess

        try:
            df_result = subprocess.run(
                [
                    "df",
                    "-kT",
                    "--exclude-type=tmpfs",
                    "--exclude-type=devtmpfs",
                    "--exclude-type=squashfs",
                ],
                capture_output=True,
                text=True,
                shell=False,
            )
            if df_result.returncode != 0:
                df_result = subprocess.run(
                    ["df", "-k"], capture_output=True, text=True, shell=False
                )
            raw = df_result.stdout
        except FileNotFoundError:
            raw = ""

        disks: list[DiskInfo] = []
        for line in raw.splitlines()[1:]:
            parts = line.split()
            if len(parts) < 7:
                # Fallback for df without -T
                if len(parts) >= 6:
                    device, total_s, used_s, avail_s, pct_s, mount = (
                        parts[0],
                        parts[1],
                        parts[2],
                        parts[3],
                        parts[4],
                        parts[5],
                    )
                    fstype = ""
                else:
                    continue
            else:
                device, fstype, total_s, used_s, avail_s, pct_s, mount = (
                    parts[0],
                    parts[1],
                    parts[2],
                    parts[3],
                    parts[4],
                    parts[5],
                    parts[6],
                )
            try:
                total = int(total_s) * 1024
                used = int(used_s) * 1024
                free = int(avail_s) * 1024
            except ValueError:
                continue
            try:
                percent = float(pct_s.rstrip("%"))
            except ValueError:
                percent = 0.0
            disks.append(
                DiskInfo(
                    device=device,
                    mountpoint=mount,
                    fstype=fstype,
                    total_bytes=total,
                    used_bytes=used,
                    free_bytes=free,
                    percent_used=percent,
                )
            )
        return disks

    # ── Services ────────────────────────────────────────────────────

    def get_services(self, pattern: str = "") -> list[ServiceInfo]:
        import subprocess

        try:
            systemctl_result = subprocess.run(
                [
                    "systemctl",
                    "list-units",
                    "--type=service",
                    "--no-pager",
                    "--no-legend",
                ],
                capture_output=True,
                text=True,
                shell=False,
            )
            raw = systemctl_result.stdout
        except FileNotFoundError:
            raw = ""
        services: list[ServiceInfo] = []
        for line in raw.splitlines():
            parts = line.split(None, 4)
            if len(parts) < 4:
                continue
            unit_name = parts[0]
            active = parts[2]  # active/inactive
            if pattern and pattern.lower() not in unit_name.lower():
                continue
            status = (
                ServiceStatus.RUNNING if active == "active" else ServiceStatus.STOPPED
            )
            services.append(
                ServiceInfo(
                    name=unit_name.removesuffix(".service"),
                    status=status,
                    pid=None,
                    enabled=status == ServiceStatus.RUNNING,
                )
            )
        return services

    # ── Network ─────────────────────────────────────────────────────

    def get_network_interfaces(self) -> list[NetworkInfo]:
        # Try ip command first, fall back to ifconfig
        import subprocess

        try:
            ip_result = subprocess.run(
                ["ip", "-o", "addr", "show"],
                capture_output=True,
                text=True,
                shell=False,
            )
            raw = ip_result.stdout
        except FileNotFoundError:
            raw = ""
        interfaces: list[NetworkInfo] = []

        if raw:
            seen: dict[str, NetworkInfo] = {}
            for line in raw.splitlines():
                parts = line.split()
                if len(parts) < 4:
                    continue
                iface = parts[1]
                family = parts[2]  # inet / inet6
                if family != "inet":
                    continue
                addr = parts[3].split("/")[0]
                if iface not in seen:
                    seen[iface] = NetworkInfo(
                        interface=iface,
                        ip_address=addr,
                        mac_address="",
                        is_up=True,
                    )
            # Get MAC addresses
            try:
                link_result = subprocess.run(
                    ["ip", "-o", "link", "show"],
                    capture_output=True,
                    text=True,
                    shell=False,
                )
                link_raw = link_result.stdout
            except FileNotFoundError:
                link_raw = ""
            for line in link_raw.splitlines():
                m_iface = re.match(r"^\d+:\s+(\S+):", line)
                m_mac = re.search(r"link/ether\s+([0-9a-f:]+)", line)
                if m_iface and m_mac:
                    iface = m_iface.group(1)
                    if iface in seen:
                        seen[iface] = NetworkInfo(
                            interface=iface,
                            ip_address=seen[iface].ip_address,
                            mac_address=m_mac.group(1),
                            is_up="UP" in line,
                        )
            interfaces = list(seen.values())
        else:
            # Fallback: ifconfig
            try:
                ifconfig_result = subprocess.run(
                    ["ifconfig", "-a"],
                    capture_output=True,
                    text=True,
                    shell=False,
                )
                raw = ifconfig_result.stdout
            except FileNotFoundError:
                raw = ""
            current_iface = ""
            ip_addr = ""
            mac_addr = ""
            is_up = False
            for line in raw.splitlines():
                m = re.match(r"^(\w[\w\d]*):.*", line)
                if m:
                    if current_iface:
                        interfaces.append(
                            NetworkInfo(
                                interface=current_iface,
                                ip_address=ip_addr,
                                mac_address=mac_addr,
                                is_up=is_up,
                            )
                        )
                    current_iface = m.group(1)
                    ip_addr = ""
                    mac_addr = ""
                    is_up = "UP" in line
                    continue
                stripped = line.strip()
                if stripped.startswith("inet "):
                    ip_addr = (
                        stripped.split()[1].split(":")[1]
                        if ":" in stripped.split()[1]
                        else stripped.split()[1]
                    )
                elif "HWaddr" in stripped or "ether" in stripped:
                    parts = stripped.split()
                    mac_addr = parts[-1]
            if current_iface:
                interfaces.append(
                    NetworkInfo(
                        interface=current_iface,
                        ip_address=ip_addr,
                        mac_address=mac_addr,
                        is_up=is_up,
                    )
                )
        return interfaces
