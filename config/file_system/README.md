# File System Configuration

**Version**: v1.1.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

File system operations, directory management, and file watching. Provides safe file I/O utilities with atomic writes and directory traversal.

## Configuration Options

The file_system module operates with sensible defaults and does not require environment variable configuration. File operations use atomic writes by default to prevent corruption. Watch intervals and ignore patterns are configurable.

## MCP Tools

This module exposes 2 MCP tool(s):

- `file_read`
- `file_write`

## PAI Integration

PAI agents invoke file_system tools through the MCP bridge. File operations use atomic writes by default to prevent corruption. Watch intervals and ignore patterns are configurable.

## Validation

```bash
# Verify module is available
codomyrmex modules | grep file_system

# Run module health check
codomyrmex status
```

## Navigation

- [Source Module](../../src/codomyrmex/file_system/README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md)
