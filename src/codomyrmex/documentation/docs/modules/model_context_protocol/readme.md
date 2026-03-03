# Model Context Protocol

**Version**: v1.0.8 | **Status**: Active | **Last Updated**: March 2026

## Overview

Model Context Protocol Module for Codomyrmex.

## Architecture Overview

```
model_context_protocol/
    __init__.py              # Public API exports
    mcp_tools.py             # MCP tool definitions
```

## Key Exports

- **`MCPErrorDetail`**
- **`MCPMessage`**
- **`MCPToolCall`**
- **`MCPToolRegistry`**
- **`MCPToolResult`**
- **`MCPServer`**
- **`MCPServerConfig`**
- **`mcp_tool`**
- **`MCPClient`**
- **`MCPClientConfig`**
- **`MCPClientError`**
- **`MCPErrorCode`**
- **`MCPToolError`**
- **`FieldError`**
- **`ValidationResult`**

## MCP Tools Reference

| Tool | Trust Level |
|------|-------------|
| `inspect_server` | Safe |
| `list_registered_tools` | Safe |
| `get_tool_schema` | Safe |

## Related Modules

See [All Modules](../README.md) for the complete module listing.

## Navigation

- **Source**: [src/codomyrmex/model_context_protocol/](../../../../src/codomyrmex/model_context_protocol/)
- **Parent**: [All Modules](../README.md)
