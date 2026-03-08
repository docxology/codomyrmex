# macOS Provider - Agent Coordination

> Codomyrmex v1.1.9 | March 2026

## Overview

The macOS provider implements `OSProviderBase` using native macOS commands (`sw_vers`, `sysctl`, `ps`, `df`, `launchctl`, `ifconfig`) to gather real system information. It is auto-selected by `get_provider()` when `detect_platform()` returns `OSPlatform.MACOS`.

## Key Files

| File | Purpose |
|------|---------|
| `__init__.py` | Exports `MacOSProvider` |
| `provider.py` | `MacOSProvider` class with five abstract method implementations plus `_run()` helper |

## MCP Tools Available

The macOS provider does not expose its own MCP tools. It is consumed indirectly through the parent `operating_system` module's generic API (`get_system_info()`, `list_processes()`, `get_disk_usage()`, `get_services()`, `get_network_interfaces()`).

## Agent Instructions

1. **Never instantiate directly** -- use `operating_system.get_provider()` which auto-detects the platform and returns the correct provider instance.
2. **All commands have a 10-second timeout** -- the `_run()` helper enforces `timeout=10.0` on all subprocess calls; long-running commands will return empty strings silently.
3. **Memory is reported in bytes** -- `get_system_info().memory_total_bytes` uses `sysctl -n hw.memsize` which returns raw bytes.
4. **Uptime is calculated from boot time** -- `sysctl -n kern.boottime` returns the boot timestamp; uptime is `time.time() - boot_sec`.
5. **Filesystem type defaults to APFS** -- `get_disk_usage()` hardcodes `fstype="apfs"` since modern macOS predominantly uses APFS.

## Operating Contracts

- `MacOSProvider` implements all five abstract methods from `OSProviderBase`: `get_system_info`, `list_processes`, `get_disk_usage`, `get_services`, `get_network_interfaces`.
- The inherited concrete methods `execute_command` and `get_environment_variables` work identically across all platforms.
- Process status mapping: `S`/`I` prefix -> SLEEPING, `T` -> STOPPED, `Z` -> ZOMBIE, all others -> RUNNING.
- Service status from `launchctl list`: PID present -> RUNNING, PID is `-` -> STOPPED.

## Common Patterns

```python
from codomyrmex.operating_system import get_provider, get_system_info

# Auto-detected usage (recommended)
info = get_system_info()
print(f"{info.hostname} running macOS {info.platform_version}")

# Direct provider usage
provider = get_provider()
disks = provider.get_disk_usage()
services = provider.get_services(pattern="ssh")
```

## PAI Agent Role Access Matrix

| Agent Role | Access Level | Typical Use |
|------------|-------------|-------------|
| Engineer | Read | Query system info for environment validation |
| Architect | Read | Assess platform capabilities and constraints |
| QATester | Read | Verify system requirements before test runs |

## Navigation

- Parent: [operating_system module](../README.md)
- Sibling: [Linux provider](../linux/AGENTS.md) | [Windows provider](../windows/AGENTS.md)
- Root: [codomyrmex](../../../../README.md)
