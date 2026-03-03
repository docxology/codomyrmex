# Containerization

**Version**: v1.0.8 | **Status**: Active | **Last Updated**: March 2026

## Overview

Containerization Module for Codomyrmex.

## Architecture Overview

```
containerization/
    __init__.py              # Public API exports
    mcp_tools.py             # MCP tool definitions
```

## Key Exports

- **`cli_commands`**
- **`docker`**
- **`kubernetes`**
- **`registry`**
- **`security`**

## MCP Tools Reference

| Tool | Trust Level |
|------|-------------|
| `container_build` | Safe |
| `container_list` | Safe |
| `container_security_scan` | Safe |

## Related Modules

See [All Modules](../README.md) for the complete module listing.

## Navigation

- **Source**: [src/codomyrmex/containerization/](../../../../src/codomyrmex/containerization/)
- **Parent**: [All Modules](../README.md)
