# Agent Guidelines - Model Context Protocol

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Module Overview

MCP server/client implementation for AI agent tool access.

## Key Classes

- **MCPServer** — MCP server implementation
- **MCPClient** — Client to connect to servers
- **Tool** — Tool definition
- **Resource** — Resource definition

## Agent Instructions

1. **Define tools clearly** — Schema and descriptions
2. **Validate input** — Check tool parameters
3. **Return structured** — Consistent response format
4. **Handle errors** — Graceful error responses
5. **Document capabilities** — List all available tools

## Common Patterns

```python
from codomyrmex.model_context_protocol import (
    MCPServer, Tool, Resource, run_server
)

# Define tools
@Tool(name="search", description="Search codebase")
def search_code(query: str, limit: int = 10):
    return find_matches(query, limit)

# Create server
server = MCPServer(name="codomyrmex")
server.register_tool(search_code)

# Add resources
server.register_resource(Resource(
    uri="file:///project",
    name="Project Files",
    mimeType="text/plain"
))

# Run server
run_server(server, port=8080)

# Client usage
client = MCPClient("http://localhost:8080")
result = client.call_tool("search", query="function")
```

## Testing Patterns

```python
# Verify tool registration
server = MCPServer("test")
server.register_tool(search_code)
assert "search" in server.list_tools()

# Verify tool execution
result = server.call_tool("search", query="test")
assert result is not None
```

## MCP Tools Available

All tools are auto-discovered via `@mcp_tool` decorators and exposed through the MCP bridge.

| Tool | Description | Trust Level |
|------|-------------|-------------|
| `inspect_server` | Inspect the running MCP server's configuration and state | Safe |
| `list_registered_tools` | List all tools registered across the MCP ecosystem | Safe |
| `get_tool_schema` | Get the JSON schema for a specific registered MCP tool | Safe |

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)
