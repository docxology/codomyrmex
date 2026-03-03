# Validation

**Version**: v1.0.8 | **Status**: Active | **Last Updated**: March 2026

## Overview

Validation utilities for system integrity and integration.

## Architecture Overview

```
validation/
    __init__.py              # Public API exports
    mcp_tools.py             # MCP tool definitions
```

## Key Exports

- **`validate_pai_integration`**
- **`Result`**
- **`ResultStatus`**

## MCP Tools Reference

| Tool | Trust Level |
|------|-------------|
| `validate_schema` | Safe |
| `validate_config` | Safe |
| `validation_summary` | Safe |

## Related Modules

See [All Modules](../README.md) for the complete module listing.

## Navigation

- **Source**: [src/codomyrmex/validation/](../../../../src/codomyrmex/validation/)
- **Parent**: [All Modules](../README.md)
