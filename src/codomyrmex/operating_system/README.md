# Operating System Module

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: March 2026

Cross-platform operating system abstraction with generic methods and platform-specific submodules for macOS, Linux, and Windows.

## PAI Integration

| Algorithm Phase | Role | Tools Used |
|----------------|------|-----------|
| **OBSERVE** | Gather system info, detect platform, enumerate processes | `os_system_info`, `os_list_processes` |
| **PLAN** | Check disk space and network before resource-heavy tasks | `os_disk_usage`, `os_network_info` |
| **VERIFY** | Confirm command execution results | `os_execute_command` |

## Installation

```bash
uv sync
```

No external dependencies — uses `subprocess` + native OS commands only.

## Key Exports

### Enums

- **`OSPlatform`** — `MACOS`, `LINUX`, `WINDOWS`, `UNKNOWN`
- **`ServiceStatus`** — `RUNNING`, `STOPPED`, `UNKNOWN`
- **`ProcessStatus`** — `RUNNING`, `SLEEPING`, `STOPPED`, `ZOMBIE`, `UNKNOWN`

### Data Models

- **`SystemInfo`** — hostname, platform, architecture, CPU, memory, kernel, uptime
- **`ProcessInfo`** — pid, name, status, cpu_percent, memory, user, command
- **`DiskInfo`** — device, mountpoint, fstype, total/used/free bytes, percent
- **`ServiceInfo`** — name, status, pid, enabled
- **`NetworkInfo`** — interface, IP, MAC, is_up
- **`CommandResult`** — command, exit_code, stdout, stderr, duration_ms

### Generic Functions

- **`detect_platform()`** — Detect current OS
- **`get_provider()`** — Get platform-specific provider (cached)
- **`get_system_info()`** — System info for current platform
- **`list_processes(limit=50)`** — Running processes
- **`get_disk_usage()`** — Mounted filesystem usage
- **`get_services(pattern="")`** — System services
- **`get_network_interfaces()`** — Network interface info
- **`execute_command(cmd, timeout=30)`** — Run a shell command
- **`get_environment_variables(prefix="")`** — Env vars

## Quick Start

```python
from codomyrmex.operating_system import (
    detect_platform, get_system_info, list_processes,
    get_disk_usage, execute_command,
)

# Detect current platform
print(detect_platform())  # OSPlatform.MACOS

# System information
info = get_system_info()
print(f"{info.hostname} — {info.architecture} — {info.cpu_count} cores")

# Running processes
for proc in list_processes(limit=10):
    print(f"  [{proc.pid}] {proc.name}")

# Disk usage
for disk in get_disk_usage():
    print(f"  {disk.mountpoint}: {disk.percent_used}%")

# Execute a command
result = execute_command("echo hello")
print(result.stdout)  # "hello"
```

## Platform Submodules

| Platform | Provider | Native Commands |
|----------|----------|----------------|
| macOS | `MacOSProvider` | `sw_vers`, `sysctl`, `ps`, `df`, `launchctl`, `ifconfig` |
| Linux | `LinuxProvider` | `/proc`, `uname`, `df`, `systemctl`, `ip`, `ps` |
| Windows | `WindowsProvider` | `wmic`, `PowerShell`, `tasklist`, `Get-Service`, `Get-NetAdapter` |

## Testing

```bash
uv run python -m pytest src/codomyrmex/tests/unit/operating_system/ -v
```

## Documentation

- [Agent Guide](AGENTS.md) | [Specification](SPEC.md) | [PAI](PAI.md)
