<!-- markdownlint-disable MD060 -->

# Windows Provider - Technical Specification

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: May 2026

> Codomyrmex v1.1.9 | March 2026

## Overview

The Windows provider (`WindowsProvider`) is a concrete implementation of `OSProviderBase` that uses native Windows commands and PowerShell cmdlets to gather real-time system information without external dependencies.

## Design Principles

1. **Native-first** -- stable Win32 APIs and native commands are preferred for
   core system and process data; PowerShell remains the interface for richer
   service, disk, network, and uptime queries.
2. **Current Windows compatibility** -- physical memory uses
   `GlobalMemoryStatusEx` because WMIC is not installed by default on current
   Windows releases.
3. **Extended timeouts** -- 15-second default timeout (vs 10 on Unix) to account for PowerShell startup latency.
4. **Zero external dependencies** -- only Python standard-library modules and
   Windows-native interfaces are required.

## Architecture

```text
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
| memory_total_bytes | Win32 `GlobalMemoryStatusEx` | 0 |
| uptime_seconds | PowerShell `gcim Win32_OperatingSystem` | 0.0 |

### list_processes(limit: int = 50) -> list[ProcessInfo]

- Command: `tasklist /FO CSV /NH`
- Parses CSV output for PID, image name, and working-set memory.
- Omits the Windows scheduler pseudo-process at PID 0 so every returned
  `ProcessInfo` satisfies the shared positive-PID contract.
- Localized memory separators and unit text are normalized before conversion to bytes.
- CPU usage is reported as `0.0` because `tasklist` does not expose a stable
  instantaneous CPU percentage.
- All returned entries are reported as RUNNING because `tasklist` lists active processes.

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
| `csv` | Parse stable `tasklist` CSV output |
| `ctypes` | Call `GlobalMemoryStatusEx` |
| `os` | `cpu_count()` |
| `platform` | Hostname, version, release info |
| `re` | Parse command output |
| `subprocess` | Execute system commands via `_run()` |
| `operating_system.base` | `OSProviderBase` and all data model types |

## Constraints

- Requires PowerShell 3.0+ for `Get-NetAdapter` and `Get-NetIPAddress`.
- `_run()` uses `shell=True` which invokes `cmd.exe` as the command interpreter.
- 15-second timeout may be insufficient on systems with antivirus scanning of process creation.

## Navigation

- Parent: [operating_system module](../README.md)
- Sibling: [macOS provider](../mac/SPEC.md) | [Linux provider](../linux/SPEC.md)
- Root: [codomyrmex](../../../../README.md)

## Related Documents

- **Agents**: [AGENTS.md](AGENTS.md)
