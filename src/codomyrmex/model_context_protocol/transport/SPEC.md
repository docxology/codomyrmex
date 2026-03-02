# Transport — Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Server and client implementations for MCP communication over stdio and HTTP transports. The server processes JSON-RPC 2.0 messages for tool execution, resource access, and prompt rendering. The client connects to external MCP servers with retry, connection pooling, and health checks.

## Architecture

- **Server**: `MCPServer` dispatches JSON-RPC methods (`initialize`, `tools/list`, `tools/call`, `resources/list`, `resources/read`, `prompts/list`, `prompts/get`) to internal handlers. Embeds `MCPToolRegistry` for tool management and `RateLimiter` for request throttling. HTTP mode uses FastAPI with Streamable HTTP at `/mcp` plus REST convenience endpoints.
- **Client**: `MCPClient` uses pluggable `_Transport` implementations (`_StdioTransport`, `_HTTPTransport`) behind async context manager factories. Automatic retry with exponential backoff for transient errors.
- **Entry point**: `main.py` late-loads Core-layer MCP tool modules to respect layer boundaries, registers their `@mcp_tool` functions, then starts the server.

## Key Classes

### `MCPServer`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `tool` | `name, description, title, output_schema` | Decorator | Register a tool via decorator; auto-generates inputSchema from type hints |
| `register_tool` | `name, schema, handler, title, output_schema` | `None` | Register a tool programmatically |
| `register_resource` | `uri, name, description, mime_type, content_provider` | `None` | Register a URI-addressable resource |
| `register_file_resource` | `path: str` | `None` | Register a local file as a resource with auto-detected MIME type |
| `register_prompt` | `name, description, arguments, template` | `None` | Register a prompt template with `{key}` substitution |
| `handle_request` | `message: dict, correlation_id: str | None` | `dict | None` | Process a JSON-RPC message; returns `None` for notifications |
| `run_stdio` | — | `None` (async) | Read JSON-RPC from stdin, write responses to stdout |
| `run_http` | `host, port` | `None` (async) | Start FastAPI server with `/mcp`, `/tools`, `/resources`, `/prompts`, `/health` endpoints |
| `run` | — | `None` | Synchronous entry point (runs stdio) |

### `MCPServerConfig`

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `name` | `str` | `"codomyrmex-mcp-server"` | Server identity |
| `version` | `str` | `"1.0.0"` | Server version |
| `transport` | `str` | `"stdio"` | Transport type |
| `default_tool_timeout` | `float` | `60.0` | Per-tool execution timeout (seconds) |
| `per_tool_timeouts` | `dict[str, float] | None` | Per-tool timeout overrides |
| `rate_limit_rate` | `float` | `50.0` | Global rate (req/s) |
| `rate_limit_burst` | `int` | `100` | Global burst ceiling |
| `warm_up` | `bool` | `True` | Eagerly populate discovery cache |

### `MCPClient`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `connect_stdio` | `command: list[str], config` | Context manager | Connect to stdio MCP server subprocess |
| `connect_http` | `base_url: str, config` | Context manager | Connect to HTTP MCP server |
| `initialize` | — | `dict` | Perform MCP initialize handshake |
| `health_check` | — | `dict` | Ping server; returns latency and status |
| `list_tools` | — | `list[dict]` | List server tools |
| `call_tool` | `name, arguments, timeout` | `dict` | Invoke a tool with optional timeout override |
| `list_resources` | — | `list[dict]` | List server resources |
| `read_resource` | `uri: str` | `dict` | Read a resource by URI |
| `list_prompts` | — | `list[dict]` | List prompt templates |
| `get_prompt` | `name, arguments` | `dict` | Get a rendered prompt |
| `close` | — | `None` | Close the connection |

### `MCPClientConfig`

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `timeout_seconds` | `float` | `30.0` | Default per-request timeout |
| `max_retries` | `int` | `3` | Max retry attempts |
| `retry_delay` | `float` | `0.5` | Base delay between retries (doubled each attempt) |
| `connection_pool_size` | `int` | `10` | Max simultaneous HTTP connections |
| `protocol_version` | `str` | `"2025-06-18"` | MCP protocol version to negotiate |

## Dependencies

- **Internal**: `codomyrmex.logging_monitoring`, `model_context_protocol.schemas.mcp_schemas`, `model_context_protocol.reliability.rate_limiter`, `model_context_protocol.quality.validation`, `model_context_protocol.errors`
- **External**: `fastapi`, `uvicorn` (HTTP server), `aiohttp` (HTTP client transport), standard library (`asyncio`, `json`)

## Constraints

- HTTP client transport requires `aiohttp`; raises `MCPClientError` if not installed.
- HTTP server transport requires `fastapi` and `uvicorn`.
- `main.py` Core-layer modules (`coding`, `containerization`, `git_operations`, `search`) are loaded lazily to respect layer boundaries.
- Tool execution uses `run_in_executor` for synchronous handlers with `asyncio.wait_for` timeout enforcement.
- Zero-mock: real network/process I/O only, `NotImplementedError` for unimplemented paths.

## Error Handling

- `MCPServer._call_tool` returns structured `MCPToolError` responses for validation failures, rate limiting, timeouts, and execution errors.
- `MCPClient._send` retries on `TimeoutError`, `OSError`, `ConnectionError`; raises `MCPClientError` after exhausting retries.
- `MCPClientError` raised for JSON-RPC error responses from the server.
- All errors logged before propagation.
