# Windows Provider - Technical Specification

> Codomyrmex v1.1.9 | March 2026

## Overview

The Windows provider (`WindowsProvider`) is a concrete implementation of `OSProviderBase` that uses native Windows commands and PowerShell cmdlets to gather real-time system information without external dependencies.

## Design Principles

1. **PowerShell-first** -- most system queries use PowerShell one-liners via `_powershell()`, providing structured output that is easier to parse than legacy command output.
2. **Legacy fallbacks** -- `wmic` is used for memory information where PowerShell alternatives may not be available on older systems.
3. **Extended timeouts** -- 15-second default timeout (vs 10 on Unix) to account for PowerShell startup latency.
4. **Zero external dependencies** -- only `os`, `platform`, `re`, `subprocess` from the standard library.

## Architecture

```
windows/
    __init__.py     # Re-exports WindowsProvider
    provider.py     # WindowsProvider(OSProviderBase) + _run() + _powershell() helpers
```

`WindowsProvider` inherits from `OSProviderBase` (defined in `operating_system/base.py`) and implements all five abstract methods.

## Functional Requirements

### get_system_info() -> SystemInfo

| Data | Source | Fallback |
|------|--------|----------|
| hostname | `platform.node()` | -- |
| platform_version | `platform.version()` | -- |
| kernel_version | `platform.release()` | -- |
| cpu_count | `os.cpu_count()` | 1 |
| memory_total_bytes | `wmic ComputerSystem get TotalPhysicalMemory` | 0 |
| uptime_seconds | PowerShell `gcim Win32_OperatingSystem` | 0.0 |

### list_processes(limit: int = 50) -> list[ProcessInfo]

- Command: PowerShell `Get-Process | Select-Object Id, ProcessName, CPU, WorkingSet64`
- Parses structured output for PID, name, CPU, and memory.
- Memory from `WorkingSet64` is already in bytes.
- All processes reported as RUNNING (PowerShell `Get-Process` only returns running processes).

### get_disk_usage() -> list[DiskInfo]

- Command: PowerShell `Get-PSDrive -PSProvider FileSystem`
- Reports `Used` and `Free` in bytes.
- `fstype` set to `"NTFS"` by default.
- `mountpoint` is the drive root (e.g., `C:\`).

### get_services(pattern: str = "") -> list[ServiceInfo]

- Command: PowerShell `Get-Service`
- Parses `Status` and `Name` columns.
- Case-insensitive pattern filtering on service name.
- `Running` -> RUNNING; all other states -> STOPPED.

### get_network_interfaces() -> list[NetworkInfo]

- Commands: PowerShell `Get-NetAdapter` + `Get-NetIPAddress -AddressFamily IPv4`
- `Get-NetAdapter` provides interface name, MAC address, and UP/DOWN status.
- `Get-NetIPAddress` provides IPv4 addresses mapped by interface alias.
- Requires PowerShell 3.0+ with NetAdapter module.

## Interface Contracts

- All methods return the data model types defined in `operating_system/base.py`.
- `_run(cmd, timeout=15.0)` returns `str` -- empty string on any error.
- `_powershell(script, timeout=15.0)` wraps `_run()` with `powershell -NoProfile -Command`.
- No method raises exceptions to the caller; errors produce empty/zero/default values.

## Dependencies

| Dependency | Purpose |
|------------|---------|
| `os` | `cpu_count()` |
| `platform` | Hostname, version, release info |
| `re` | Parse command output |
| `subprocess` | Execute system commands via `_run()` |
| `operating_system.base` | `OSProviderBase` and all data model types |

## Constraints

- Requires PowerShell 3.0+ for `Get-NetAdapter` and `Get-NetIPAddress`.
- `wmic` is deprecated on Windows 10 21H1+ but still functional; may need replacement with PowerShell `Get-CimInstance` in future versions.
- `_run()` uses `shell=True` which invokes `cmd.exe` as the command interpreter.
- 15-second timeout may be insufficient on systems with antivirus scanning of process creation.

## Navigation

- Parent: [operating_system module](../README.md)
- Sibling: [macOS provider](../mac/SPEC.md) | [Linux provider](../linux/SPEC.md)
- Root: [codomyrmex](../../../../README.md)
