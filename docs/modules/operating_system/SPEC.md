# Operating System Specification

**Version**: v1.1.4 | **Status**: Active | **Last Updated**: March 2026

## Overview

Provides cross-platform operating system abstraction with auto-detection and platform-specific providers for macOS, Linux, and Windows. Offers unified APIs for system info, process management, disk usage, service listing, network interfaces, and command execution.

## Functional Requirements

1. Auto-detect OSPlatform (macOS, Linux, Windows) and dispatch to correct provider
2. System information retrieval: hostname, CPU count, memory, kernel, uptime
3. Process listing, disk usage reporting, service enumeration, and network interface queries
4. Command execution with timeout and structured CommandResult output


## Interface

```python
from codomyrmex.operating_system import detect_platform, get_system_info, list_processes, get_disk_usage

platform = detect_platform()
info = get_system_info()
procs = list_processes(limit=20)
disks = get_disk_usage()
```

## Exports

OSPlatform, SystemInfo, ProcessInfo, DiskInfo, ServiceInfo, NetworkInfo, CommandResult, detect_platform, get_provider, get_system_info, list_processes, get_disk_usage, get_services, get_network_interfaces, execute_command, get_environment_variables

## Navigation

- [Source README](../../src/codomyrmex/operating_system/README.md) | [AGENTS.md](AGENTS.md)
