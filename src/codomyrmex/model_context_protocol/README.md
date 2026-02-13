# model_context_protocol

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Foundation-layer module defining the Model Context Protocol (MCP), the standardized communication specification between AI agents and platform tools within Codomyrmex. Provides JSON-RPC message handling, Pydantic-validated schemas for tool calls, and a full MCP server implementation with stdio transport.

## Quick Start

```python
from codomyrmex.model_context_protocol import MCPServer, MCPToolRegistry

# Create an MCP server
server = MCPServer()

# Register a tool using decorator
@server.tool(name="search", description="Search the database")
def search(query: str) -> str:
    return f"Results for: {query}"

# Register a resource
server.register_resource(
    uri="file:///data/config.json",
    name="Configuration",
    description="App configuration file"
)

# Run the server (stdio transport)
server.run()
```


## Installation

```bash
uv add codomyrmex
```

Or for development:

```bash
uv sync
```

## Key Exports

### Server Classes

- **`MCPServer`** -- Full MCP server with tool, resource, and prompt support
- **`MCPServerConfig`** -- Configuration for server name, version, transport

### Schema Classes

- **`MCPErrorDetail`** -- Structured error information
- **`MCPMessage`** -- Protocol message representation
- **`MCPToolCall`** -- Tool invocation with `tool_name` and `arguments`
- **`MCPToolRegistry`** -- Registry for available tools
- **`MCPToolResult`** -- Tool execution result with status validation

### Submodules

- **`schemas`** -- Pydantic schema definitions
- **`adapters`** -- Protocol adapters for external systems
- **`validators`** -- Message validation utilities
- **`discovery`** -- Tool discovery mechanisms

## CLI Scripts

```bash
# Run MCP server for Claude Desktop
python scripts/model_context_protocol/run_mcp_server.py

# List available tools
python scripts/model_context_protocol/run_mcp_server.py --list-tools
```

## Claude Desktop Integration

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "codomyrmex": {
      "command": "python",
      "args": ["/path/to/codomyrmex/scripts/model_context_protocol/run_mcp_server.py"]
    }
  }
}
```


## Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k model_context_protocol -v
```

## Navigation

- **Full Documentation**: [docs/modules/model_context_protocol/](../../../docs/modules/model_context_protocol/)
- **Scripts**: [scripts/model_context_protocol/](../../../scripts/model_context_protocol/)
- **LLM Integration**: [llm/mcp.py](../llm/mcp.py)
- **Parent Directory**: [codomyrmex](../README.md)
