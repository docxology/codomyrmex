# Events

**Version**: v1.0.8 | **Status**: Active | **Last Updated**: March 2026

## Overview

Event-Driven Architecture for Codomyrmex

## Architecture Overview

```
events/
    __init__.py              # Public API exports
    mcp_tools.py             # MCP tool definitions
```

## Key Exports

- **`notification`**
- **`streaming`**

## MCP Tools Reference

| Tool | Trust Level |
|------|-------------|
| `emit_event` | Safe |
| `list_event_types` | Safe |
| `get_event_history` | Safe |

## Related Modules

See [All Modules](../README.md) for the complete module listing.

## Navigation

- **Source**: [src/codomyrmex/events/](../../../../src/codomyrmex/events/)
- **Parent**: [All Modules](../README.md)
