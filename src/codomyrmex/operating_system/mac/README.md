# macOS Provider

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: March 2026

macOS-specific implementation of the operating system provider. Uses native macOS commands (`sw_vers`, `sysctl`, `ps`, `df`, `launchctl`, `ifconfig`) for real system queries.

## Key Exports

| Export | Type | Description |
|--------|------|-------------|
| `MacOSProvider` | Class | macOS implementation of `OSProviderBase` |

## Native Commands Used

| Function | Command | Fallback |
|----------|---------|----------|
| `get_system_info()` | `sw_vers`, `sysctl -n hw.memsize`, `sysctl -n kern.boottime` | `platform.mac_ver()` |
| `list_processes()` | `ps -eo pid,stat,user,%cpu,rss,comm` | — |
| `get_disk_usage()` | `df -k -T nodevfs,autofs,map` | — |
| `get_services()` | `launchctl list` | — |
| `get_network_interfaces()` | `ifconfig -a` | — |

## Navigation

- [Parent README](../README.md) | [Parent SPEC](../SPEC.md)
