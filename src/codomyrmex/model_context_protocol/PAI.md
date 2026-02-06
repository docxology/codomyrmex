# Personal AI Infrastructure — Model Context Protocol Module

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The Model Context Protocol module provides PAI integration for MCP server and client operations.

## PAI Capabilities

### MCP Server

Run an MCP server:

```python
from codomyrmex.model_context_protocol import MCPServer

server = MCPServer()
server.register_tool("search", search_function)
server.register_resource("config", config_data)
server.start(port=8080)
```

### MCP Client

Connect to MCP servers:

```python
from codomyrmex.model_context_protocol import MCPClient

client = MCPClient("http://localhost:8080")
result = client.call_tool("search", query="hello")
```

## PAI Integration Points

| Component | PAI Use Case |
|-----------|-------------|
| `MCPServer` | Host tools |
| `MCPClient` | Use tools |
| `Resources` | Share resources |

## Navigation

- [README](README.md) | [AGENTS](AGENTS.md) | [SPEC](SPEC.md)
