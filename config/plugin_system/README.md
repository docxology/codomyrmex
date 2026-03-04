# Plugin System Configuration

**Version**: v1.1.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Plugin discovery, dependency resolution, and lifecycle management. Provides entry point scanning and plugin dependency graph resolution.

## Configuration Options

The plugin_system module operates with sensible defaults and does not require environment variable configuration. Plugin directories and entry point groups are configurable. Plugin loading order respects dependency resolution.

## MCP Tools

This module exposes 2 MCP tool(s):

- `plugin_scan_entry_points`
- `plugin_resolve_dependencies`

## PAI Integration

PAI agents invoke plugin_system tools through the MCP bridge. Plugin directories and entry point groups are configurable. Plugin loading order respects dependency resolution.

## Validation

```bash
# Verify module is available
codomyrmex modules | grep plugin_system

# Run module health check
codomyrmex status
```

## Navigation

- [Source Module](../../src/codomyrmex/plugin_system/README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md)
