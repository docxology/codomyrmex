# Security

**Version**: v1.0.8 | **Status**: Active | **Last Updated**: March 2026

## Overview

Security Module for Codomyrmex.

## Architecture Overview

```
security/
    __init__.py              # Public API exports
    mcp_tools.py             # MCP tool definitions
```

## Key Exports

- **`governance`**

## MCP Tools Reference

| Tool | Trust Level |
|------|-------------|
| `scan_vulnerabilities` | Safe |
| `scan_secrets` | Safe |
| `audit_code_security` | Safe |

## Related Modules

See [All Modules](../README.md) for the complete module listing.

## Navigation

- **Source**: [src/codomyrmex/security/](../../../../src/codomyrmex/security/)
- **Parent**: [All Modules](../README.md)
