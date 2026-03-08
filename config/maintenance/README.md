# Maintenance Configuration

**Version**: v1.1.9 | **Status**: Active | **Last Updated**: March 2026

## Overview

System health checks and task management. Provides maintenance_health_check for system status and maintenance_list_tasks for tracking maintenance activities.

## Configuration Options

The maintenance module operates with sensible defaults and does not require environment variable configuration. Health check thresholds (disk space, memory, CPU) are configurable. Task retention period is set through the maintenance manager.

## MCP Tools

This module exposes 2 MCP tool(s):

- `maintenance_health_check`
- `maintenance_list_tasks`

## PAI Integration

PAI agents invoke maintenance tools through the MCP bridge. Health check thresholds (disk space, memory, CPU) are configurable. Task retention period is set through the maintenance manager.

## Validation

```bash
# Verify module is available
codomyrmex modules | grep maintenance

# Run module health check
codomyrmex status
```

## Navigation

- [Source Module](../../src/codomyrmex/maintenance/README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md)
