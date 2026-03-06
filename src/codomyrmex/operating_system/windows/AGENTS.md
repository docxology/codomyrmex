# Windows Provider - Agent Coordination

> Codomyrmex v1.1.4 | March 2026

## Overview

The Windows provider implements `OSProviderBase` using native Windows commands (`wmic`, `systeminfo`) and PowerShell cmdlets (`Get-Process`, `Get-PSDrive`, `Get-Service`, `Get-NetAdapter`, `Get-NetIPAddress`) to gather real system information. It is auto-selected by `get_provider()` when `detect_platform()` returns `OSPlatform.WINDOWS`.

## Key Files

| File | Purpose |
|------|---------|
| `__init__.py` | Exports `WindowsProvider` |
| `provider.py` | `WindowsProvider` class with five abstract method implementations, `_run()` and `_powershell()` helpers |

## MCP Tools Available

The Windows provider does not expose its own MCP tools. It is consumed indirectly through the parent `operating_system` module's generic API (`get_system_info()`, `list_processes()`, `get_disk_usage()`, `get_services()`, `get_network_interfaces()`).

## Agent Instructions

1. **Never instantiate directly** -- use `operating_system.get_provider()` which auto-detects the platform and returns the correct provider instance.
2. **PowerShell is the primary command interface** -- the `_powershell()` helper runs one-liners via `powershell -NoProfile -Command`, with a 15-second timeout.
3. **`wmic` is used for memory info** -- `wmic ComputerSystem get TotalPhysicalMemory` provides total physical memory; this command is deprecated in newer Windows versions but remains functional.
4. **Service management uses Get-Service** -- `get_services()` calls the PowerShell `Get-Service` cmdlet and maps `Running` status to RUNNING, all others to STOPPED.
5. **Network interfaces use Get-NetAdapter** -- combined with `Get-NetIPAddress` for IP addresses; both require PowerShell 3.0+.

## Operating Contracts

- `WindowsProvider` implements all five abstract methods from `OSProviderBase`: `get_system_info`, `list_processes`, `get_disk_usage`, `get_services`, `get_network_interfaces`.
- The inherited concrete methods `execute_command` and `get_environment_variables` work identically across all platforms.
- `_run()` uses 15-second timeout (vs 10 seconds on macOS/Linux) to account for typically slower Windows command startup.
- `_powershell()` wraps `_run()` with `powershell -NoProfile -Command` prefix.

## Common Patterns

```python
from codomyrmex.operating_system import get_provider, get_system_info

# Auto-detected usage (recommended)
info = get_system_info()
print(f"{info.hostname}: Windows {info.platform_version}")

# Direct provider usage
provider = get_provider()
services = provider.get_services(pattern="sql")
disks = provider.get_disk_usage()
```

## PAI Agent Role Access Matrix

| Agent Role | Access Level | Typical Use |
|------------|-------------|-------------|
| Engineer | Read | Query system info for Windows-specific development |
| Architect | Read | Assess Windows platform capabilities |
| QATester | Read | Verify Windows-specific test prerequisites |

## Navigation

- Parent: [operating_system module](../README.md)
- Sibling: [macOS provider](../mac/AGENTS.md) | [Linux provider](../linux/AGENTS.md)
- Root: [codomyrmex](../../../../README.md)
