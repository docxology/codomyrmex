# Codomyrmex Agents — src/codomyrmex/model_context_protocol/transport

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Implements the MCP server and client for both stdio and HTTP transports. The server handles JSON-RPC 2.0 requests for tool execution, resource management, and prompt templates with integrated rate limiting, argument validation, and per-tool timeouts. The client consumes external MCP servers with automatic retry, connection pooling, and health checks.

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `server.py` | `MCPServer` | Full MCP server: tool/resource/prompt management, JSON-RPC dispatch, stdio and HTTP (FastAPI + Streamable HTTP) transports |
| `server.py` | `MCPServerConfig` | Server configuration: name, version, transport type, timeouts, rate limits, warm-up flag |
| `client.py` | `MCPClient` | Client for consuming MCP servers; supports stdio and HTTP via `connect_stdio()` / `connect_http()` context managers |
| `client.py` | `MCPClientConfig` | Client configuration: timeout, retries, retry delay, protocol version, connection pool size |
| `client.py` | `MCPClientError` | Exception for client-side errors |
| `client.py` | `_StdioTransport` / `_HTTPTransport` | Internal transport implementations for subprocess stdin/stdout and HTTP (aiohttp) |
| `main.py` | `run_server()` | Entry point that creates `MCPServer`, late-loads Core-layer MCP tool modules, registers their `@mcp_tool` functions, and starts stdio transport |
| `main.py` | `main()` | Synchronous wrapper (`asyncio.run(run_server())`) |
| `web_ui.py` | `get_web_ui_html()` | Returns HTML for the browser-based MCP server UI |

## Operating Contracts

- `MCPServer._call_tool` validates arguments via `validate_tool_arguments()` before dispatch; returns structured `MCPToolError` on validation failure.
- Per-tool timeouts are enforced via `asyncio.wait_for` with `config.per_tool_timeouts` overrides.
- Rate limiting is applied per tool call via the embedded `RateLimiter` instance.
- `MCPClient._send()` retries on `TimeoutError`, `OSError`, and `ConnectionError` with exponential backoff up to `max_retries`.
- `main.py` late-loads Core-layer modules (`coding`, `containerization`, `git_operations`, `search`) inside `run_server()` to respect Foundation-to-Core layer boundaries.
- HTTP transport supports MCP 2025-06-18 protocol version with `title` and `outputSchema`/`structuredContent` fields.
- Errors must be logged via `logging_monitoring` before re-raising.

## Integration Points

- **Depends on**: `codomyrmex.logging_monitoring` (structured logging, correlation IDs), `model_context_protocol.schemas.mcp_schemas` (`MCPToolCall`, `MCPToolRegistry`), `model_context_protocol.reliability.rate_limiter` (`RateLimiter`), `model_context_protocol.quality.validation` (`validate_tool_arguments`), `model_context_protocol.errors` (structured error types)
- **Used by**: CLI entry points, PAI MCP bridge (may start server), any external MCP client connecting over stdio or HTTP
- **External**: `fastapi`, `uvicorn` (HTTP transport), `aiohttp` (HTTP client)

## Navigation

- **Parent**: [model_context_protocol](../README.md)
- **Root**: [Root](../../../../README.md)
