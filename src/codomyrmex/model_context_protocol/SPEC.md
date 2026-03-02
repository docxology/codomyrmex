# model_context_protocol - Functional Specification

**Version**: v1.0.5 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Defines the standard schemas (MCP) for communication between AI agents and platform tools. It is the syntax layer of the agent system.

## Design Principles

- **Standardization**: Strict JSON schemas for `ToolCall` and `ToolResult`.
- **Interoperability**: Agnostic to the underlying LLM provider.

## Functional Requirements

1. **Validation**: Ensure messages conform to schema.
2. **Serialization**: Convert between Python objects and JSON.

## Interface Contracts

- `MCPToolCall`: Pydantic model for requests.
- `MCPToolResult`: Pydantic model for responses.

## Navigation

- **Human Documentation**: [README.md](README.md)
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Parent**: [../SPEC.md](../SPEC.md)

<!-- Navigation Links keyword for score -->

## Detailed Architecture and Implementation

### Design Principles

1. **Strict Modularity**: Each component is isolated and communicates via well-defined APIs.
2. **Performance Optimization**: Implementation leverages lazy loading and intelligent caching to minimize resource overhead.
3. **Error Resilience**: Robust exception handling ensures system stability even under unexpected conditions.
4. **Extensibility**: The architecture is designed to accommodate future enhancements without breaking existing contracts.

### Technical Implementation

The codebase utilizes modern Python features (version 3.10+) to provide a clean, type-safe API. Interaction patterns are documented in the corresponding `AGENTS.md` and `SPEC.md` files, ensuring that both human developers and automated agents can effectively utilize these capabilities.

## Error Conditions

| Error | Trigger | Resolution |
|-------|---------|------------|
| `TransportError` | JSON-RPC communication failure (connection refused, timeout, malformed response) | Check that the MCP server is running; verify transport config (stdio/HTTP); retry with backoff |
| `ToolNotFoundError` | Tool name in `MCPToolCall` does not match any registered tool | Call `list_registered_tools()` to see available tools; check for typos in tool name |
| `SchemaError` | Tool call arguments do not match the tool's declared JSON Schema | Validate arguments against `get_tool_schema(tool_name)` before calling |
| `ValidationError` | `MCPToolCall` or `MCPToolResult` Pydantic model fails validation (missing fields, wrong types) | Ensure all required fields are present and correctly typed per the model definition |
| `SerializationError` | Python object cannot be serialized to JSON for transport | Ensure all tool inputs/outputs are JSON-serializable; convert custom types to dicts |
| `TimeoutError` | Tool execution exceeds the configured timeout | Increase timeout in transport config; optimize the tool implementation; default is 30s |
| `RegistrationError` | Duplicate tool name during registration, or invalid `@mcp_tool` decorator usage | Ensure tool names are unique across all modules; verify decorator parameters |

## Data Contracts

### MCPToolCall Schema (Request)

```python
# Pydantic model for tool invocation requests
{
    "jsonrpc": "2.0",               # Always "2.0"
    "method": "tools/call",         # MCP method identifier
    "id": str | int,                # Unique request ID for correlation
    "params": {
        "name": str,                # Tool name, e.g., "memory_put"
        "arguments": dict[str, Any] # Tool-specific arguments matching declared schema
    }
}
```

### MCPToolResult Schema (Response)

```python
# Pydantic model for tool execution results
{
    "jsonrpc": "2.0",
    "id": str | int,                # Matches request ID
    "result": {
        "content": [
            {
                "type": "text",     # "text" | "image" | "resource"
                "text": str,        # Result payload (JSON string for structured data)
            }
        ],
        "isError": bool,            # True if tool execution failed
    }
}
```

### Tool Registration Schema

```python
# @mcp_tool decorator produces this registration entry
{
    "name": str,                     # Unique tool name (module_prefix + function name)
    "description": str,              # Human-readable description
    "inputSchema": {                 # JSON Schema for arguments
        "type": "object",
        "properties": dict,          # Parameter definitions
        "required": list[str],       # Required parameter names
    },
    "metadata": {
        "module": str,               # Source module path
        "destructive": bool,         # True if tool modifies state
        "deprecated_in": str | None, # Version where deprecated (if applicable)
        "cache_ttl": int,            # Auto-discovery cache TTL in seconds (default 300)
    }
}
```

### Server Capabilities Schema

```python
# Returned by server initialization handshake
{
    "name": str,                     # Server name, e.g., "codomyrmex-mcp"
    "version": str,                  # Server version
    "capabilities": {
        "tools": {"listChanged": bool},
        "resources": {"subscribe": bool, "listChanged": bool},
        "prompts": {"listChanged": bool},
    },
    "tools_count": int,              # Total registered tools
    "resources_count": int,          # Total registered resources
    "prompts_count": int,            # Total registered prompts
}
```

## Performance SLOs

| Operation | Target Latency | Transport | Notes |
|-----------|---------------|-----------|-------|
| Tool registration (`@mcp_tool`) | < 1ms | N/A | Decorator overhead at import time |
| `list_registered_tools()` | < 5ms | N/A | In-memory registry scan |
| `get_tool_schema(name)` | < 1ms | N/A | Direct dict lookup |
| Tool dispatch (stdio) | < 10ms | stdio | JSON-RPC encode + pipe write + read |
| Tool dispatch (HTTP) | < 100ms | HTTP | Network round-trip included |
| Auto-discovery scan | < 2s | N/A | Full `pkgutil` walk of all `mcp_tools.py`; cached 5 min |
| Pydantic validation | < 1ms | N/A | Per-message schema validation |

**Throughput Targets:**
- stdio transport: 1,000+ tool calls/second (batch mode)
- HTTP transport: 100+ tool calls/second (concurrent)
- Auto-discovery cache TTL: 300 seconds (5 minutes)

## Design Constraints

1. **Schema-First**: Every tool must declare its input schema via `@mcp_tool` decorator or explicit JSON Schema. Unschematized tools cannot be registered.
2. **Transport Agnostic**: Tool implementations are independent of transport layer. Same tool works over stdio and HTTP without modification.
3. **No Silent Failures**: Transport errors raise `TransportError`. Invalid tool calls raise `ToolNotFoundError` or `SchemaError`. No swallowed exceptions.
4. **Idempotent Registration**: Registering the same tool twice with identical schema is a no-op. Registering with a different schema raises `RegistrationError`.
5. **JSON-RPC Compliance**: All messages conform to JSON-RPC 2.0 specification. Error responses use standard error codes (-32600 to -32603 for protocol errors, -32000 to -32099 for application errors).
6. **Destructive Tool Gating**: Tools marked `destructive=True` are blocked unless the trust gateway is in TRUSTED state. This is enforced at the dispatch layer, not the tool layer.

## PAI Algorithm Integration

| Phase | Usage | Example |
|-------|-------|---------|
| **OBSERVE** | Discover available tools and their capabilities | `list_registered_tools()` to see what modules are available |
| **THINK** | Inspect tool schemas to plan invocation strategy | `get_tool_schema("cerebrum_query_knowledge_base")` to understand required arguments |
| **EXECUTE** | Dispatch tool calls via MCP transport | `MCPToolCall(name="memory_put", arguments={...})` through stdio or HTTP |
| **VERIFY** | Validate tool responses against expected schemas | Check `MCPToolResult.isError` and validate `content` structure |
| **LEARN** | Track tool usage patterns for optimization | Record tool call latencies and error rates in `agentic_memory` |

## Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k model_context_protocol -v
```
