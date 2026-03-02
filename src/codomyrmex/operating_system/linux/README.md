# Linux Provider

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: March 2026

Linux-specific implementation of the operating system provider. Uses native Linux commands and `/proc` filesystem for real system queries.

## Key Exports

| Export | Type | Description |
|--------|------|-------------|
| `LinuxProvider` | Class | Linux implementation of `OSProviderBase` |

## Native Commands Used

| Function | Command | Fallback |
|----------|---------|----------|
| `get_system_info()` | `/etc/os-release`, `/proc/meminfo`, `/proc/uptime`, `uname -r` | `platform.release()` |
| `list_processes()` | `ps -eo pid,stat,user,%cpu,rss,comm --no-headers` | — |
| `get_disk_usage()` | `df -kT --exclude-type=tmpfs` | `df -k` |
| `get_services()` | `systemctl list-units --type=service` | — |
| `get_network_interfaces()` | `ip -o addr show`, `ip -o link show` | `ifconfig -a` |

## Navigation

- [Parent README](../README.md) | [Parent SPEC](../SPEC.md)
