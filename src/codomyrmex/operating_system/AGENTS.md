# Agent Guidelines — Operating System

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: March 2026

## Module Overview

Cross-platform OS abstraction. Auto-detects platform and dispatches to macOS / Linux / Windows providers.

## Key Classes

- **`OSProviderBase`** — Abstract base for platform providers
- **`MacOSProvider`** / **`LinuxProvider`** / **`WindowsProvider`** — Concrete implementations
- **`SystemInfo`** / **`ProcessInfo`** / **`DiskInfo`** / **`ServiceInfo`** / **`NetworkInfo`** — Data models

## Agent Instructions

1. **Use generic functions** — Always prefer `get_system_info()` over direct provider instantiation
2. **Cache results** — `get_provider()` is cached; no need to store the provider yourself
3. **Check disk before I/O** — Use `get_disk_usage()` before large writes
4. **Exec sparingly** — `execute_command()` runs real commands; validate input
5. **Filter env vars** — Use `prefix=` to limit scope when inspecting environment

## Common Patterns

```python
from codomyrmex.operating_system import (
    detect_platform, get_system_info, list_processes,
    execute_command, get_environment_variables,
)

# Quick system check
platform = detect_platform()
info = get_system_info()
print(f"{platform.value}: {info.hostname}")

# Safe command execution
result = execute_command("whoami")
if result.success:
    print(result.stdout)

# Environment inspection
path_vars = get_environment_variables(prefix="PATH")
```

## MCP Tools Available

| Tool | Description | Trust Level |
|------|-------------|-------------|
| `os_system_info` | System information (hostname, CPU, memory, kernel) | Safe |
| `os_list_processes` | Running processes with CPU/memory stats | Safe |
| `os_disk_usage` | Disk usage for mounted filesystems | Safe |
| `os_network_info` | Network interface details | Safe |
| `os_execute_command` | Execute a shell command | Observed |
| `os_environment_variables` | Environment variable inspection | Safe |

## PAI Agent Role Access Matrix

| PAI Agent | Access Level | Primary Capabilities | Trust Level |
|-----------|-------------|---------------------|-------------|
| **Engineer** | Full | All MCP tools; system command execution | TRUSTED |
| **Architect** | Read | `os_system_info`, `os_disk_usage`, `os_network_info`; capacity planning | OBSERVED |
| **QATester** | Validation | `os_system_info`, `os_list_processes`; environment verification | OBSERVED |

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)
