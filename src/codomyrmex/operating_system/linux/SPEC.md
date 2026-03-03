# Linux Provider - Technical Specification

> Codomyrmex v1.0.8 | March 2026

## Overview

The Linux provider (`LinuxProvider`) is a concrete implementation of `OSProviderBase` that uses native Linux system commands and the `/proc` filesystem to gather real-time system information without external dependencies.

## Design Principles

1. **Native commands and /proc filesystem** -- uses `uname`, `/etc/os-release`, `/proc/meminfo`, `/proc/uptime`, `ps`, `df`, `systemctl`, `ip`, and `ifconfig` through `subprocess.run()`.
2. **Dual-path fallbacks** -- network interfaces try `ip` command first, falling back to `ifconfig`; disk usage falls back from `df -kT` to `df -k`.
3. **Zero external dependencies** -- only `os`, `platform`, `re`, `subprocess` from the standard library.

## Architecture

```
linux/
    __init__.py     # Re-exports LinuxProvider
    provider.py     # LinuxProvider(OSProviderBase) + _run() helper
```

`LinuxProvider` inherits from `OSProviderBase` (defined in `operating_system/base.py`) and implements all five abstract methods.

## Functional Requirements

### get_system_info() -> SystemInfo

| Data | Source | Fallback |
|------|--------|----------|
| hostname | `platform.node()` | -- |
| platform_version | `/etc/os-release` `PRETTY_NAME` | `uname -r` |
| kernel_version | `uname -r` | `platform.release()` |
| cpu_count | `os.cpu_count()` | 1 |
| memory_total_bytes | `/proc/meminfo` `MemTotal` (kB -> bytes) | 0 |
| uptime_seconds | `/proc/uptime` first field | 0.0 |

### list_processes(limit: int = 50) -> list[ProcessInfo]

- Command: `ps -eo pid,stat,user,%cpu,rss,comm --no-headers | head -n {limit}`
- Parses 6 whitespace-delimited columns per line.
- RSS converted from KB to bytes (`int(rss) * 1024`).
- Status mapping: `S` -> SLEEPING, `T` -> STOPPED, `Z` -> ZOMBIE, default -> RUNNING.

### get_disk_usage() -> list[DiskInfo]

- Primary: `df -kT --exclude-type=tmpfs --exclude-type=devtmpfs --exclude-type=squashfs`
- Fallback: `df -k` (7-column vs 6-column parsing).
- All sizes in KB, converted to bytes.
- `fstype` read from the second column when `-T` is available; empty string otherwise.

### get_services(pattern: str = "") -> list[ServiceInfo]

- Command: `systemctl list-units --type=service --no-pager --no-legend`
- Parses unit name (column 0) and active state (column 2).
- Case-insensitive pattern filtering on unit name.
- `active` -> RUNNING; all other states -> STOPPED.
- `.service` suffix stripped from names.

### get_network_interfaces() -> list[NetworkInfo]

Primary path (`ip` command available):
- `ip -o addr show` for interface names and IPv4 addresses.
- `ip -o link show` for MAC addresses and UP status.
- Only `inet` (IPv4) addresses collected; `inet6` skipped.

Fallback path (`ifconfig`):
- `ifconfig -a` parsed line by line.
- Interface headers detected by regex `^(\w[\w\d]*):.*`.
- `HWaddr` or `ether` lines for MAC; `inet` lines for IP.

## Interface Contracts

- All methods return the data model types defined in `operating_system/base.py`.
- `_run(cmd, timeout=10.0)` returns `str` -- empty string on any error.
- No method raises exceptions to the caller; errors produce empty/zero/default values.

## Dependencies

| Dependency | Purpose |
|------------|---------|
| `os` | `cpu_count()`, `path.basename()` |
| `platform` | Fallback hostname and release info |
| `re` | Parse `ip` output for interface names and MAC addresses |
| `subprocess` | Execute system commands via `_run()` |
| `operating_system.base` | `OSProviderBase` and all data model types |

## Constraints

- `systemctl` is required for service listing; systems without systemd return empty lists.
- `/proc` filesystem must be mounted for memory and uptime information.
- `_run()` uses `shell=True` with 10-second default timeout.
- The `ip` command is preferred over `ifconfig`; both must be in `$PATH`.

## Navigation

- Parent: [operating_system module](../README.md)
- Sibling: [macOS provider](../mac/SPEC.md) | [Windows provider](../windows/SPEC.md)
- Root: [codomyrmex](../../../../README.md)
