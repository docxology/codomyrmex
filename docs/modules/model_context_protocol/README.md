# Model Context Protocol Documentation

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

MCP implementation for AI tool and resource sharing.

## Key Features

- **Servers** — MCP server implementation
- **Clients** — MCP client connections
- **Tools** — Tool registration
- **Resources** — Resource sharing

## Quick Start

```python
from codomyrmex.model_context_protocol import MCPServer

server = MCPServer()
server.register_tool("search", search_function)
server.start(port=8080)
```

## Directory Contents

| File | Description |
|------|-------------|
| `README.md` | This file |
| `SPEC.md` | Technical specification |

## Navigation

- **Source**: [src/codomyrmex/model_context_protocol/](../../../src/codomyrmex/model_context_protocol/)
- **Parent**: [Modules](../README.md)
