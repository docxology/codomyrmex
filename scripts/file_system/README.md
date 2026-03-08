# File System Scripts

**Version**: v1.1.9 | **Status**: Active | **Last Updated**: March 2026

## Overview

Utility scripts for the `file_system` module, which provides cross-platform file system operations including file creation, directory management, and path manipulation.

## Purpose

These scripts provide a CLI interface for common file system operations using the `FileSystemManager` from the codomyrmex file_system module. They serve as both operational utilities and integration demonstrations.

## Contents

| File | Description |
|------|-------------|
| `fs_utils.py` | CLI-driven file system operations using `create_file_system_manager()` factory |

## Usage

**Prerequisites:**
```bash
uv sync
```

**Run:**
```bash
uv run python scripts/file_system/fs_utils.py <command> [options]
```

## Agent Usage

Agents performing file operations should prefer the MCP tools (`file_system` module) over direct filesystem calls. This script demonstrates the correct factory pattern for obtaining a `FileSystemManager` instance.

## Related Module

- Source: `src/codomyrmex/file_system/`
- MCP Tools: via `file_system/mcp_tools.py`

## Navigation

- [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md) | [PAI.md](PAI.md)
- [Parent: scripts/](../README.md)
