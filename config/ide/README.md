# IDE Configuration

**Version**: v1.1.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

IDE integration and Antigravity client for editor communication. Provides file tracking, artifact management, and IDE bridge for development workflows.

## Configuration Options

The ide module operates with sensible defaults and does not require environment variable configuration. IDE bridge automatically detects running editor instances. Antigravity client uses artifact mtime and cwd scan for file resolution.

## MCP Tools

This module exposes 2 MCP tool(s):

- `ide_get_active_file`
- `ide_list_open_files`

## PAI Integration

PAI agents invoke ide tools through the MCP bridge. IDE bridge automatically detects running editor instances. Antigravity client uses artifact mtime and cwd scan for file resolution.

## Validation

```bash
# Verify module is available
codomyrmex modules | grep ide

# Run module health check
codomyrmex status
```

## Navigation

- [Source Module](../../src/codomyrmex/ide/README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md)
