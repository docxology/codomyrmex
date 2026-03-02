# Schemas — Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Core data models for MCP communication. Two layers: lightweight dataclass models for general use (`__init__.py`) and Pydantic-validated models for strict protocol compliance (`mcp_schemas.py`).

## Architecture

Dual-model design:

- **Dataclass models** (`__init__.py`): Zero-dependency content types, tool definitions, messages, conversations, and request/response envelopes. All provide `to_dict()` for JSON serialization.
- **Pydantic models** (`mcp_schemas.py`): Strict validation with cross-field validators for protocol compliance. `MCPToolRegistry` provides an in-memory registry with handler dispatch.

## Key Classes

### Dataclass Models (`__init__.py`)

#### `Tool`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `to_dict` | — | `dict` | Serialize to plain dict |
| `to_openai_format` | — | `dict` | Convert to OpenAI function calling format with JSON Schema properties |

#### `ToolParameter`

| Field | Type | Description |
|-------|------|-------------|
| `name` | `str` | Parameter name |
| `param_type` | `str` | JSON Schema type (string, number, boolean, array, object) |
| `description` | `str` | Human-readable description |
| `required` | `bool` | Whether the parameter is required (default `True`) |
| `default` | `Any` | Default value |
| `enum` | `list[Any] | None` | Allowed values |

#### `Message`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `from_text` | `role: MessageRole, text: str` | `Message` | Factory for simple text messages |
| `get_text` | — | `str` | Extract and join all `TextContent` from the message |

#### `Conversation`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `add_user_message` | `text: str` | `None` | Append a USER text message |
| `add_assistant_message` | `text: str` | `None` | Append an ASSISTANT text message |
| `to_json` | — | `str` | Full JSON serialization |

### Pydantic Models (`mcp_schemas.py`)

#### `MCPToolResult`

| Field | Type | Validation |
|-------|------|------------|
| `status` | `str` | Required |
| `data` | `dict | None` | Must be null/omitted on failure status |
| `error` | `MCPErrorDetail | None` | Must be populated on failure status |
| `explanation` | `str | None` | Optional human-readable explanation |

#### `MCPToolRegistry`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `register` | `tool_name, schema, handler` | `None` | Register a tool with schema and handler |
| `unregister` | `tool_name: str` | `bool` | Remove a tool; returns `True` if found |
| `get` | `tool_name: str` | `dict | None` | Look up tool metadata |
| `list_tools` | — | `list[str]` | List all registered tool names |
| `validate_call` | `tool_call: MCPToolCall` | `tuple[bool, str | None]` | Check if tool exists |
| `execute` | `tool_call: MCPToolCall` | `MCPToolResult` | Dispatch to handler; wrap exceptions in error result |

## Dependencies

- **Internal**: `codomyrmex.logging_monitoring`
- **External**: `pydantic` (for `mcp_schemas.py`), standard library (`json`, `datetime`, `enum`, `dataclasses`)

## Constraints

- Pydantic models use `ConfigDict(extra="allow")` to permit tool-specific extra fields.
- Cross-field validators in `MCPToolResult` enforce consistency between `status`, `data`, and `error`.
- Zero-mock: real data only, `NotImplementedError` for unimplemented paths.

## Error Handling

- `MCPToolRegistry.execute()` catches all handler exceptions and returns `MCPToolResult(status="failure")` with `MCPErrorDetail`.
- Pydantic `ValidationError` raised when cross-field constraints are violated (e.g., failure status without error).
- All errors logged before propagation.
