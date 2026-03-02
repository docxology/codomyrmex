# Model Context Protocol Module

**Version**: v1.0.5 | **Status**: Active | **Last Updated**: March 2026

## Overview

Foundation-layer module defining the Model Context Protocol (MCP), the standardized communication specification between AI agents and platform tools within Codomyrmex. Provides JSON-RPC message handling, Pydantic-validated schemas for tool calls, and a full MCP server implementation with stdio transport.

## PAI Integration

| Algorithm Phase | Role | Tools Used |
|----------------|------|-----------|
| **ALL PHASES** | MCP is the transport layer -- all PAI-codomyrmex communication flows through it | `inspect_server`, `list_registered_tools` |
| **OBSERVE** | Discover available tools and their schemas | `list_registered_tools`, `get_tool_schema` |
| **VERIFY** | Confirm MCP server health and tool availability | `inspect_server` |

This module **is** the integration layer. PAI agents communicate with codomyrmex exclusively via MCP (JSON-RPC over stdio or HTTP). `inspect_server` provides health checks; `list_registered_tools` enumerates the 171 available tools; `get_tool_schema` validates tool interfaces. The trust gateway (`trust_gateway.py`) gates destructive tool access.

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

## Dynamic Discovery (New)

The module supports decentralized tool registration via decorators, allowing any Python function in the codebase to be exposed as an MCP tool without centralized registration.

```python
from codomyrmex.model_context_protocol.decorators import mcp_tool

@mcp_tool(category="data_analysis")
def analyze_data(filepath: str) -> dict:
    """Analyze a data file."""
    # ... implementation
```

The PAI Bridge (`src/codomyrmex/agents/pai/mcp_bridge.py`) automatically discovers these tools in key modules (`visualization`, `llm`, `security`, `agentic_memory`).
