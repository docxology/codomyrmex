# Linux Provider - Agent Coordination

> Codomyrmex v1.0.8 | March 2026

## Overview

The Linux provider implements `OSProviderBase` using native Linux commands and the `/proc` filesystem to gather real system information. It is auto-selected by `get_provider()` when `detect_platform()` returns `OSPlatform.LINUX`.

## Key Files

| File | Purpose |
|------|---------|
| `__init__.py` | Exports `LinuxProvider` |
| `provider.py` | `LinuxProvider` class with five abstract method implementations plus `_run()` helper |

## MCP Tools Available

The Linux provider does not expose its own MCP tools. It is consumed indirectly through the parent `operating_system` module's generic API (`get_system_info()`, `list_processes()`, `get_disk_usage()`, `get_services()`, `get_network_interfaces()`).

## Agent Instructions

1. **Never instantiate directly** -- use `operating_system.get_provider()` which auto-detects the platform and returns the correct provider instance.
2. **Network interface detection has two paths** -- `get_network_interfaces()` tries `ip -o addr show` first, falling back to `ifconfig -a` if the `ip` command is unavailable.
3. **Memory comes from /proc/meminfo** -- reported in kB by the kernel, converted to bytes by multiplying by 1024.
4. **Uptime comes from /proc/uptime** -- the first floating-point value in the file, representing seconds since boot.
5. **Service management uses systemctl** -- `get_services()` calls `systemctl list-units --type=service`; on systems without systemd, the method returns an empty list.

## Operating Contracts

- `LinuxProvider` implements all five abstract methods from `OSProviderBase`: `get_system_info`, `list_processes`, `get_disk_usage`, `get_services`, `get_network_interfaces`.
- The inherited concrete methods `execute_command` and `get_environment_variables` work identically across all platforms.
- Process status mapping: `S` prefix -> SLEEPING, `T` -> STOPPED, `Z` -> ZOMBIE, all others -> RUNNING.
- Service status: `active` -> RUNNING, all other states -> STOPPED.
- `_run()` uses 10-second timeout; all exceptions return empty string.

## Common Patterns

```python
from codomyrmex.operating_system import get_provider, get_system_info

# Auto-detected usage (recommended)
info = get_system_info()
print(f"{info.hostname}: {info.platform_version}")

# Direct provider usage
provider = get_provider()
processes = provider.list_processes(limit=20)
interfaces = provider.get_network_interfaces()
```

## PAI Agent Role Access Matrix

| Agent Role | Access Level | Typical Use |
|------------|-------------|-------------|
| Engineer | Read | Query system info for CI/CD environment validation |
| Architect | Read | Assess server platform capabilities |
| QATester | Read | Verify Linux-specific test prerequisites |

## Navigation

- Parent: [operating_system module](../README.md)
- Sibling: [macOS provider](../mac/AGENTS.md) | [Windows provider](../windows/AGENTS.md)
- Root: [codomyrmex](../../../../README.md)
