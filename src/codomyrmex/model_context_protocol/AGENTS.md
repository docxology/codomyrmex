# Agent Guidelines - Model Context Protocol

**Version**: v1.0.5 | **Status**: Active | **Last Updated**: March 2026

## Module Overview

Foundation-layer module implementing the Model Context Protocol (MCP) — the JSON-RPC communication standard between PAI agents and Codomyrmex tools. Provides Pydantic-validated schemas, `@mcp_tool` decorator for auto-discovery, full MCP server with stdio/HTTP transport, and three introspection tools for discovering and inspecting all registered tools at runtime. Every PAI-codomyrmex call flows through this module's transport layer.

## Key Files

| File | Purpose |
|------|---------|
| `__init__.py` | Exports `MCPServer`, `MCPToolRegistry`, `MCPMessage`, `MCPToolCall`, `MCPToolResult` |
| `decorators.py` | `@mcp_tool` decorator — tag any function for auto-discovery |
| `discovery/` | `pkgutil`-based discovery scanning all `mcp_tools.py` submodules |
| `adapters/` | Protocol adapters for external systems |
| `quality/` | Message validation utilities |
| `reliability/` | Transport reliability helpers |
| `mcp_tools.py` | Self-referential MCP introspection tools |

## Key Classes

- **`MCPServer`** — Full MCP server with tool, resource, and prompt registration; stdio/HTTP transport
- **`MCPToolRegistry`** — Registry mapping tool names to callables and schemas
- **`MCPMessage`** — JSON-RPC message representation
- **`MCPToolCall`** — Tool invocation with `tool_name` and `arguments`
- **`MCPToolResult`** — Execution result with status validation
- **`MCPServerConfig`** — Server name, version, transport configuration

## Agent Instructions

1. **Use `@mcp_tool` decorator** — Tag functions for auto-discovery; avoid manual registration
2. **Validate input schemas** — Always use Pydantic-validated `MCPToolCall` for tool calls
3. **Return structured dicts** — All tools must return `{"status": "ok"|"error", ...}`
4. **Use `inspect_server` first** — Verify server health before long agent workflows
5. **Use `list_registered_tools`** — To discover which tools are available in the current deployment

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

## PAI Agent Role Access Matrix

| PAI Agent | Access Level | MCP Tools | Trust Level |
|-----------|-------------|-----------|-------------|
| **Engineer** | Full introspection | `inspect_server`, `list_registered_tools`, `get_tool_schema` | TRUSTED |
| **Architect** | Tool inventory | `list_registered_tools`, `get_tool_schema` | OBSERVED |
| **QATester** | Health + discovery | `inspect_server`, `list_registered_tools` | OBSERVED |
| **Researcher** | Schema inspection | `list_registered_tools`, `get_tool_schema` | OBSERVED |

### Engineer Agent
**Access**: Full MCP introspection — server state, tool registry, and schema details.
**Use Cases**: Debugging MCP bridge configuration, verifying that auto-discovered tools are registered correctly after module additions, checking tool schema validity during development.

### Architect Agent
**Access**: Tool inventory — list and inspect tools without server state access.
**Use Cases**: Auditing the full tool surface (171 tools), designing tool groupings, verifying that new `@mcp_tool` decorators produce correct schemas, planning trust-level assignments.

### QATester Agent
**Access**: Health and discovery — server health and tool registration verification.
**Use Cases**: Confirming MCP bridge starts and serves tools correctly, verifying that the expected number of tools (171 total) are registered after deployment, regression testing auto-discovery.

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)


## Rule Reference

This module is governed by the following rule file:

- [`src/codomyrmex/agentic_memory/rules/modules/model_context_protocol.cursorrules`](src/codomyrmex/agentic_memory/rules/modules/model_context_protocol.cursorrules)
