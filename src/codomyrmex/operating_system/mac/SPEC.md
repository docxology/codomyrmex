# macOS Provider - Technical Specification

> Codomyrmex v1.1.4 | March 2026

## Overview

The macOS provider (`MacOSProvider`) is a concrete implementation of `OSProviderBase` that uses native macOS system commands to gather real-time system information without external dependencies.

## Design Principles

1. **Native commands only** -- uses `sw_vers`, `sysctl`, `ps`, `df`, `launchctl`, `ifconfig` through `subprocess.run()`.
2. **Graceful degradation** -- the `_run()` helper catches all exceptions and returns empty strings, with fallbacks to Python `platform` module where applicable.
3. **Zero external dependencies** -- only `os`, `platform`, `re`, `subprocess`, and `time` from the standard library.

## Architecture

```
mac/
    __init__.py     # Re-exports MacOSProvider
    provider.py     # MacOSProvider(OSProviderBase) + _run() helper
```

`MacOSProvider` inherits from `OSProviderBase` (defined in `operating_system/base.py`) and implements all five abstract methods.

## Functional Requirements

### get_system_info() -> SystemInfo

| Data | Source Command | Fallback |
|------|---------------|----------|
| hostname | `platform.node()` | -- |
| platform_version | `sw_vers -productVersion` | `platform.mac_ver()[0]` |
| kernel_version | `uname -r` | `platform.release()` |
| cpu_count | `os.cpu_count()` | 1 |
| memory_total_bytes | `sysctl -n hw.memsize` | 0 |
| uptime_seconds | `sysctl -n kern.boottime` (parsed `sec=N`) | 0.0 |

### list_processes(limit: int = 50) -> list[ProcessInfo]

- Command: `ps -eo pid,stat,user,%cpu,rss,comm | head -n {limit + 1}`
- Skips header line. Parses 6 whitespace-delimited columns.
- RSS is converted from KB to bytes (`int(rss) * 1024`).
- Status mapping: `S`/`I` -> SLEEPING, `T` -> STOPPED, `Z` -> ZOMBIE, default -> RUNNING.

### get_disk_usage() -> list[DiskInfo]

- Command: `df -k -T nodevfs,autofs,map`
- Excludes virtual filesystems (devfs, autofs, map).
- All sizes in KB from `df -k`, converted to bytes (`* 1024`).
- `fstype` hardcoded to `"apfs"` for all entries.

### get_services(pattern: str = "") -> list[ServiceInfo]

- Command: `launchctl list`
- Parses tab-delimited output: PID, status code, label.
- Case-insensitive pattern filtering on the label field.
- PID present (not `"-"`) -> RUNNING; otherwise -> STOPPED.

### get_network_interfaces() -> list[NetworkInfo]

- Command: `ifconfig -a`
- Parses interface headers (regex `^(\w[\w\d]*):.*`), `inet` lines for IP, `ether` lines for MAC.
- `is_up` derived from `"UP"` presence in interface header line.

## Interface Contracts

- All methods return the data model types defined in `operating_system/base.py`.
- `_run(cmd, timeout=10.0)` returns `str` -- empty string on any error (timeout, permission, command not found).
- No method raises exceptions to the caller; errors result in empty/zero/default values.

## Dependencies

| Dependency | Purpose |
|------------|---------|
| `os` | `cpu_count()`, `path.basename()` |
| `platform` | Fallback hostname, version, release info |
| `re` | Parse `kern.boottime` output, interface headers |
| `subprocess` | Execute system commands via `_run()` |
| `time` | Calculate uptime from boot timestamp |
| `operating_system.base` | `OSProviderBase` and all data model types |

## Constraints

- Requires macOS system commands to be available in `$PATH`.
- `_run()` uses `shell=True` -- commands are interpreted by the user's shell.
- The 10-second timeout may be insufficient for heavily loaded systems.
- `get_disk_usage()` assumes all filesystems are APFS; HFS+ or FAT volumes will show incorrect `fstype`.

## Navigation

- Parent: [operating_system module](../README.md)
- Sibling: [Linux provider](../linux/SPEC.md) | [Windows provider](../windows/SPEC.md)
- Root: [codomyrmex](../../../../README.md)
