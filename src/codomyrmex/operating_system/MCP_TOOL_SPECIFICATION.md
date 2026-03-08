# Operating System — MCP Tool Specification

**Version**: v1.1.9 | **Status**: Active | **Last Updated**: March 2026

## Overview

This document defines the MCP tools exposed by the `operating_system` module.
These tools are auto-discovered by the PAI MCP bridge via the `@mcp_tool` decorator
in `mcp_tools.py` and surfaced as part of the ~303 dynamic tools available to Claude.

The operating system module provides cross-platform system introspection tools
covering system info, process listing, disk usage, network interfaces, command
execution, and environment variables.

## Auto-Discovery

| Property | Value |
|----------|-------|
| Discovery method | `@mcp_tool` decorator scan |
| Namespace | `operating_system` |
| Trust default | Safe (except `os_execute_command`) |
| PAI bridge | `src/codomyrmex/agents/pai/mcp/` |

## Tool Reference

### `os_system_info`

**Description**: Retrieve system information for the current platform.
**Trust Level**: Safe
**Category**: data-retrieval

**Parameters**: No parameters required.

**Returns**: `dict` — Dictionary with `status`, `hostname`, `platform`, `architecture`, `CPU count`, `memory`, `kernel version`, and `uptime`.

**Example**:
```python
from codomyrmex.operating_system.mcp_tools import os_system_info

info = os_system_info()
```

---

### `os_list_processes`

**Description**: List running processes on the current platform.
**Trust Level**: Safe
**Category**: data-retrieval

**Parameters**:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `limit` | `int` | No | `50` | Maximum number of processes to return |

**Returns**: `dict` — Dictionary with `status`, `count` (int), and `processes` (list of process info dicts).

**Example**:
```python
from codomyrmex.operating_system.mcp_tools import os_list_processes

result = os_list_processes(limit=20)
```

---

### `os_disk_usage`

**Description**: Return disk usage for all mounted filesystems.
**Trust Level**: Safe
**Category**: data-retrieval

**Parameters**: No parameters required.

**Returns**: `dict` — Dictionary with `status`, `count` (int), and `disks` (list of disk usage entry dicts).

**Example**:
```python
from codomyrmex.operating_system.mcp_tools import os_disk_usage

result = os_disk_usage()
```

---

### `os_network_info`

**Description**: Return network interface information.
**Trust Level**: Safe
**Category**: data-retrieval

**Parameters**: No parameters required.

**Returns**: `dict` — Dictionary with `status`, `count` (int), and `interfaces` (list of network interface dicts).

**Example**:
```python
from codomyrmex.operating_system.mcp_tools import os_network_info

result = os_network_info()
```

---

### `os_execute_command`

**Description**: Execute a shell command on the current platform.
**Trust Level**: Safe (no explicit `trust_level="destructive"` in decorator, but executes arbitrary commands)
**Category**: data-mutation

**Parameters**:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `command` | `str` | Yes | -- | The shell command to execute |
| `timeout` | `float` | No | `30.0` | Timeout in seconds |

**Returns**: `dict` — Dictionary with `status`, command output, exit code, and timing.

**Example**:
```python
from codomyrmex.operating_system.mcp_tools import os_execute_command

result = os_execute_command(command="uname -a", timeout=10.0)
```

**Notes**: Executes arbitrary shell commands. While no explicit `trust_level="destructive"` is set in the decorator, this tool can perform system-modifying operations. Use with caution.

---

### `os_environment_variables`

**Description**: Return current environment variables, optionally filtered by prefix.
**Trust Level**: Safe
**Category**: data-retrieval

**Parameters**:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `prefix` | `str` | No | `""` | Optional prefix to filter variables (e.g. `"PATH"`, `"PYTHON"`) |

**Returns**: `dict` — Dictionary with `status`, `count` (int), and `variables` (dict of matching environment variables).

**Example**:
```python
from codomyrmex.operating_system.mcp_tools import os_environment_variables

result = os_environment_variables(prefix="PYTHON")
```

## Integration Notes

- **Auto-discovered**: Yes (via `@mcp_tool` in `mcp_tools.py`)
- **Trust Gateway**: Most tools are safe. `os_execute_command` can run arbitrary shell commands but does not have explicit destructive trust marking in the decorator.
- **PAI Phases**: OBSERVE (system introspection), EXECUTE (command execution)
- **Dependencies**: `operating_system.detector` (get_system_info, list_processes, get_disk_usage, get_network_interfaces, execute_command, get_environment_variables)

## Navigation

- [README.md](README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md)
