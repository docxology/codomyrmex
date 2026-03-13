# Operating System - API Specification

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: March 2026

## 1. Overview
The `operating_system` module provides cross-platform OS abstraction with auto-detection and platform-specific providers for macOS, Linux, and Windows. Zero external dependencies — uses `subprocess` and native OS commands.

## 2. Core Components

### 2.1 Generic API Functions

| Function | Signature | Description |
|----------|-----------|-------------|
| `detect_platform` | `() -> OSPlatform` | Auto-detect the current OS platform |
| `get_provider` | `() -> OSProviderBase` | Get the platform-specific provider (cached) |
| `get_system_info` | `() -> SystemInfo` | Full system information (hostname, CPU, memory, etc.) |
| `list_processes` | `(limit=None) -> list[ProcessInfo]` | List running processes |
| `get_disk_usage` | `() -> list[DiskInfo]` | Disk usage for all mounted volumes |
| `get_services` | `() -> list[ServiceInfo]` | List system services and their status |
| `get_network_interfaces` | `() -> list[NetworkInfo]` | List network interfaces with addresses |
| `execute_command` | `(cmd, ...) -> CommandResult` | Run a shell command and capture output |
| `get_environment_variables` | `() -> dict` | Get all environment variables |

### 2.2 Data Models

| Class | Description |
|-------|-------------|
| `SystemInfo` | System metadata (hostname, OS, CPU count, total memory) |
| `ProcessInfo` | Process details (PID, name, CPU%, memory) |
| `DiskInfo` | Disk partition usage (mount, total, used, free) |
| `ServiceInfo` | Service details (name, status, PID) |
| `NetworkInfo` | Network interface details (name, address, MAC) |
| `CommandResult` | Command execution result (stdout, stderr, returncode) |

### 2.3 Enums

| Enum | Values |
|------|--------|
| `OSPlatform` | MACOS, LINUX, WINDOWS |
| `ProcessStatus` | RUNNING, SLEEPING, STOPPED, ZOMBIE |
| `ServiceStatus` | RUNNING, STOPPED, UNKNOWN |

### 2.4 Base Class

| Class | Description |
|-------|-------------|
| `OSProviderBase` | Abstract base for platform-specific providers |

## 3. Usage Example

```python
from codomyrmex.operating_system import detect_platform, get_system_info, list_processes

platform = detect_platform()
print(f"Running on: {platform.value}")

info = get_system_info()
print(f"CPUs: {info.cpu_count}, Memory: {info.total_memory_gb:.1f} GB")

processes = list_processes(limit=5)
for p in processes:
    print(f"[{p.pid}] {p.name}")
```

## 4. Navigation

- [README](README.md) | [SPEC](SPEC.md) | [AGENTS](AGENTS.md) | [PAI](PAI.md)
