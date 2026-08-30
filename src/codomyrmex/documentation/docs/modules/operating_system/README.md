<!-- readme: generated -->

# operating_system

**Version**: v1.3.0 | **Status**: Active | **Source**: `src/codomyrmex/operating_system/`

## Overview

Codomyrmex Operating System Module.

Cross-platform operating system abstraction with generic methods and
platform-specific submodules for macOS, Linux, and Windows.

The module auto-detects the current platform and dispatches calls to
the correct provider. Generic functions work identically on every OS.

Integration:
- Uses ``subprocess`` + native OS commands (zero external dependencies).
- Providers are lazily loaded via ``get_provider()`` and cached.

Available functions (generic / cross-platform):
- detect_platform
- get_provider
- get_system_info
- list_processes
- get_disk_usage
- get_services
- get_network_interfaces
- execute_command
- get_environment_variables

## Public Exports

`operating_system` exports 20 public symbols via `__all__`:

`CommandResult`, `DiskInfo`, `NetworkInfo`, `OSPlatform`, `OSProviderBase`, `ProcessInfo`, `ProcessStatus`, `ServiceInfo`, `ServiceStatus`, `SystemInfo`, `cli_commands`, `detect_platform`, `execute_command`, `get_disk_usage`, `get_environment_variables`, `get_network_interfaces`, `get_provider`, `get_services`, `get_system_info`, `list_processes`

## Module Documentation

- Extended README: [readme.md](readme.md)
- Agent coordination: [AGENTS.md](AGENTS.md)
- Technical specification: [SPEC.md](SPEC.md)

## Navigation

- **All modules**: [../README.md](../README.md)
- **Source package**: [../../../../operating_system/](../../../../operating_system/)
