# Codomyrmex Agents — src/codomyrmex/model_context_protocol/schemas

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Defines the core data models for MCP communication: message content types, tool definitions, tool calls and results, conversations, and request/response envelopes. Provides both dataclass-based models (in `__init__.py`) for lightweight usage and Pydantic-based models (in `mcp_schemas.py`) for strict validation with field validators.

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `__init__.py` | `MessageRole` | Enum: USER, ASSISTANT, SYSTEM, TOOL |
| `__init__.py` | `ContentType` | Enum: TEXT, IMAGE, FILE, TOOL_CALL, TOOL_RESULT |
| `__init__.py` | `TextContent` / `ImageContent` / `FileContent` | Dataclass content types with `to_dict()` serialization |
| `__init__.py` | `ToolParameter` | Dataclass for tool parameter metadata; supports `to_json_schema()` conversion |
| `__init__.py` | `Tool` | Dataclass defining a tool with parameters; supports `to_openai_format()` for OpenAI function calling |
| `__init__.py` | `ToolCall` / `ToolResult` | Dataclasses for invoking tools and returning results |
| `__init__.py` | `Message` | Dataclass for conversation messages with mixed content; `from_text()` factory and `get_text()` extractor |
| `__init__.py` | `Conversation` | Ordered message collection with `add_user_message()` / `add_assistant_message()` helpers |
| `__init__.py` | `Request` / `Response` | Dataclass envelopes for model requests (with tools, temperature, max_tokens) and responses (with finish_reason, usage) |
| `__init__.py` | `create_tool()` | Factory function to build `Tool` from simplified parameter dicts |
| `mcp_schemas.py` | `MCPToolCall` | Pydantic model for tool invocations with `extra="allow"` |
| `mcp_schemas.py` | `MCPToolResult` | Pydantic model with cross-field validators: `error` required on failure, `data` null on failure |
| `mcp_schemas.py` | `MCPErrorDetail` | Pydantic model for structured error info (error_type, error_message, error_details) |
| `mcp_schemas.py` | `MCPMessage` | Pydantic model for conversation messages with tool_calls and tool_results |
| `mcp_schemas.py` | `MCPToolRegistry` | In-memory tool registry with `register`, `unregister`, `validate_call`, and `execute` methods |

## Operating Contracts

- `MCPToolResult` validators enforce that `error` is populated on failure and `data` is null on failure via `@field_validator`.
- `MCPToolRegistry.execute()` dispatches to the registered handler and wraps exceptions in `MCPToolResult` with `MCPErrorDetail`.
- Dataclass models use `to_dict()` for serialization; Pydantic models use `model_dump_json()`.
- `Tool.to_openai_format()` produces OpenAI-compatible function calling schema.
- Errors must be logged via `logging_monitoring` before re-raising.

## Integration Points

- **Depends on**: `codomyrmex.logging_monitoring` (structured logging), `pydantic` (for `mcp_schemas.py` models)
- **Used by**: `model_context_protocol.transport.server` (imports `MCPToolCall`, `MCPToolRegistry`), `model_context_protocol.quality.testing` (uses registry interface for test harnesses)

## Navigation

- **Parent**: [model_context_protocol](../README.md)
- **Root**: [Root](../../../../README.md)
