# Personal AI Infrastructure — Operating System Module

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

The Operating System module provides cross-platform system introspection for the PAI ecosystem. It enables agents to understand the host environment, monitor resources, and execute platform-appropriate commands.

## PAI Capabilities

### System Detection

```python
from codomyrmex.operating_system import detect_platform, get_system_info

platform = detect_platform()  # OSPlatform.MACOS
info = get_system_info()
# hostname, architecture, CPU, memory, kernel, uptime
```

### Resource Monitoring

```python
from codomyrmex.operating_system import get_disk_usage, list_processes

disks = get_disk_usage()
procs = list_processes(limit=20)
```

### Command Execution

```python
from codomyrmex.operating_system import execute_command

result = execute_command("git status", timeout=10)
if result.success:
    print(result.stdout)
```

## Key Exports

| Export | Type | Purpose |
|--------|------|---------|
| `detect_platform` | Function | Detect current OS platform |
| `get_system_info` | Function | Host system info |
| `list_processes` | Function | Running process enumeration |
| `get_disk_usage` | Function | Filesystem usage |
| `get_services` | Function | Service/daemon listing |
| `get_network_interfaces` | Function | Network interface info |
| `execute_command` | Function | Shell command execution |
| `get_environment_variables` | Function | Environment variable query |

## PAI Algorithm Phase Mapping

| Phase | Operating System Contribution |
|-------|-------------------------------|
| **OBSERVE** | System info + resource status at cycle start |
| **THINK** | Platform detection guides tool selection |
| **PLAN** | Disk/memory checks inform resource allocation |
| **VERIFY** | Command execution confirms changes applied |
| **LEARN** | Environment snapshots for drift detection |

## MCP Tools

| Tool | Description | Key Parameters | PAI Phase |
|------|-------------|----------------|-----------|
| `os_system_info` | Host system details | — | OBSERVE |
| `os_list_processes` | Running processes | `limit: int` | OBSERVE |
| `os_disk_usage` | Filesystem usage | — | PLAN |
| `os_network_info` | Network interfaces | — | OBSERVE |
| `os_execute_command` | Run a shell command | `command: str`, `timeout: float` | VERIFY |
| `os_environment_variables` | Environment vars | `prefix: str` | OBSERVE |

## Architecture Role

**Foundation Layer** — Provides host-level awareness. Zero codomyrmex dependencies. Consumed by `system_discovery/`, `environment_setup/`, `deployment/`, and the MCP server.

## Navigation

- **Self**: [PAI.md](PAI.md)
- **Parent**: [../PAI.md](../PAI.md) — Source-level PAI module map
- **Root Bridge**: [../../../PAI.md](../../../PAI.md) — Authoritative PAI system bridge doc
- **Siblings**: [README.md](README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md)
