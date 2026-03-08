# Events Configuration

**Version**: v1.1.9 | **Status**: Active | **Last Updated**: March 2026

## Overview

Event-driven architecture providing decoupled, asynchronous communication between components. Supports event emission, typed event registration, and event history.

## Configuration Options

The events module operates with sensible defaults and does not require environment variable configuration. Event bus is a singleton. Event types are registered dynamically. History retention can be configured through the event bus settings.

## MCP Tools

This module exposes 3 MCP tool(s):

- `emit_event`
- `list_event_types`
- `get_event_history`

## PAI Integration

PAI agents invoke events tools through the MCP bridge. Event bus is a singleton. Event types are registered dynamically. History retention can be configured through the event bus settings.

## Validation

```bash
# Verify module is available
codomyrmex modules | grep events

# Run module health check
codomyrmex status
```

## Navigation

- [Source Module](../../src/codomyrmex/events/README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md)
