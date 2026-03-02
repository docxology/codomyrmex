# operating_system — Functional Specification

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

The `operating_system` module provides a unified, cross-platform abstraction layer for querying and interacting with the host operating system. It auto-detects the current platform and dispatches to the appropriate provider (macOS, Linux, or Windows).

## Design Principles

- **Zero External Dependencies**: Uses only `subprocess` + native OS commands.
- **Platform Transparency**: Callers use the same generic API regardless of OS.
- **Lazy Provider Loading**: Platform-specific code is imported only when needed.
- **Real Data Only**: All information comes from real system queries; zero mocks.

## Functional Requirements

1. **Platform Detection**: Accurately identify macOS, Linux, or Windows.
2. **System Information**: Hostname, architecture, CPU, memory, kernel, uptime.
3. **Process Listing**: PID, name, status, CPU%, memory, user.
4. **Disk Usage**: Device, mountpoint, filesystem type, total/used/free/percent.
5. **Service Enumeration**: Name, status (running/stopped), PID, enabled flag.
6. **Network Interfaces**: Interface name, IP, MAC address, up/down status.
7. **Command Execution**: Run arbitrary shell commands with timeout and result capture.
8. **Environment Variables**: Read and filter environment variables.

## Interface Contracts

- `OSProviderBase`: Abstract base class — all platform providers must implement `get_system_info()`, `list_processes()`, `get_disk_usage()`, `get_services()`, `get_network_interfaces()`.
- `execute_command()` and `get_environment_variables()` are concrete methods on the base class.

## Data Contracts

### SystemInfo

```python
{
    "hostname": str,
    "platform": str,           # "macos" | "linux" | "windows"
    "platform_version": str,
    "architecture": str,       # "arm64" | "x86_64" | "AMD64"
    "cpu_count": int,
    "memory_total_bytes": int,
    "kernel_version": str,
    "uptime_seconds": float,
}
```

### ProcessInfo

```python
{
    "pid": int,
    "name": str,
    "status": str,             # "running" | "sleeping" | "stopped" | "zombie"
    "cpu_percent": float,
    "memory_bytes": int,
    "user": str,
    "command": str,
}
```

### DiskInfo

```python
{
    "device": str,
    "mountpoint": str,
    "fstype": str,
    "total_bytes": int,
    "used_bytes": int,
    "free_bytes": int,
    "percent_used": float,
}
```

## Error Conditions

| Error | Trigger | Resolution |
|-------|---------|------------|
| `RuntimeError` | Unsupported platform detected | Only macOS, Linux, Windows are supported |
| `subprocess.TimeoutExpired` | Command exceeds timeout | Increase timeout parameter |
| Empty results | Native command not available (e.g., `systemctl` on non-systemd Linux) | Check platform and fallback paths |

## Performance SLOs

| Operation | Target Latency | Notes |
|-----------|---------------|-------|
| `detect_platform()` | < 1ms | Pure Python, no subprocess |
| `get_system_info()` | < 500ms | 3–5 subprocess calls |
| `list_processes(50)` | < 1s | Single `ps` invocation |
| `get_disk_usage()` | < 500ms | Single `df` invocation |
| `get_services()` | < 2s | Varies by service count |
| `get_network_interfaces()` | < 500ms | 1–2 subprocess calls |

## Testing

```bash
uv run python -m pytest src/codomyrmex/tests/unit/operating_system/ -v
```

## Navigation

- **Human Documentation**: [README.md](README.md)
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Parent**: [../SPEC.md](../SPEC.md)
