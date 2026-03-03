# File System — MCP Tool Specification

**Version**: v1.0.8 | **Status**: Active | **Last Updated**: March 2026

## Overview

This document defines the MCP tools exposed by the `file_system` module.
These tools are auto-discovered by the PAI MCP bridge via the `@mcp_tool` decorator
in `mcp_tools.py` and surfaced as part of the ~303 dynamic tools available to Claude.

The file system module provides safe file reading and directory listing capabilities
for AI agents to inspect the local filesystem.

## Auto-Discovery

| Property | Value |
|----------|-------|
| Discovery method | `@mcp_tool` decorator scan |
| Namespace | `file_system` |
| Trust default | Safe |
| PAI bridge | `src/codomyrmex/agents/pai/mcp/` |

## Tool Reference

### `file_system_read`

**Description**: Read a file and return its contents.
**Trust Level**: Safe
**Category**: data-retrieval

**Parameters**:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `path` | `str` | Yes | -- | Absolute or relative path to the file to read |

**Returns**: `dict` — Dictionary with `status`, `path` (str), `content` (file contents as string), and `size_bytes` (int).

**Example**:
```python
from codomyrmex.file_system.mcp_tools import file_system_read

result = file_system_read(path="/Users/mini/Documents/GitHub/codomyrmex/pyproject.toml")
```

**Notes**: Returns an error status with message if the file is not found or cannot be read.

---

### `file_system_list_directory`

**Description**: List entries in a directory.
**Trust Level**: Safe
**Category**: data-retrieval

**Parameters**:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `path` | `str` | No | `"."` | Directory path to list (default: current working directory) |
| `recursive` | `bool` | No | `False` | If `True`, recurse into subdirectories |

**Returns**: `dict` — Dictionary with `status`, `path` (str), `recursive` (bool), `entries` (list of file/directory path strings), and `count` (int).

**Example**:
```python
from codomyrmex.file_system.mcp_tools import file_system_list_directory

result = file_system_list_directory(path="/Users/mini/Documents/GitHub/codomyrmex/src", recursive=False)
```

**Notes**: Returns an error status with message if the directory is not found.

## Integration Notes

- **Auto-discovered**: Yes (via `@mcp_tool` in `mcp_tools.py`)
- **Trust Gateway**: All tools are safe (read-only) — no trust check required
- **PAI Phases**: OBSERVE (filesystem inspection), THINK (project structure analysis)
- **Dependencies**: `file_system.FileSystemManager`

## Navigation

- [README.md](README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md)
