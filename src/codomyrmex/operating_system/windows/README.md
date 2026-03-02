# Windows Provider

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: March 2026

Windows-specific implementation of the operating system provider. Uses native Windows commands and PowerShell for real system queries.

## Key Exports

| Export | Type | Description |
|--------|------|-------------|
| `WindowsProvider` | Class | Windows implementation of `OSProviderBase` |

## Native Commands Used

| Function | Command | Fallback |
|----------|---------|----------|
| `get_system_info()` | `wmic ComputerSystem get TotalPhysicalMemory`, PowerShell `gcim` | `platform.version()` |
| `list_processes()` | PowerShell `Get-Process` | — |
| `get_disk_usage()` | PowerShell `Get-PSDrive -PSProvider FileSystem` | — |
| `get_services()` | PowerShell `Get-Service` | — |
| `get_network_interfaces()` | PowerShell `Get-NetAdapter`, `Get-NetIPAddress` | — |

## Navigation

- [Parent README](../README.md) | [Parent SPEC](../SPEC.md)
