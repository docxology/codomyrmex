# LLM Tools -- Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Tool-calling framework for LLM function calling. Provides structured tool
definitions with JSON Schema parameter types, a registry for tool management,
and serialization to OpenAI and Anthropic formats.

## Architecture

Dataclass-based design centered on `Tool`, which wraps a callable with
structured parameter metadata. `ToolRegistry` provides lookup, listing by
category, and execution. The `@tool` decorator automates `Tool` creation
from function signatures using `inspect` and `get_type_hints`.

## Key Classes

### `Tool`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `to_openai_format` | -- | `dict` | OpenAI function-calling schema |
| `to_anthropic_format` | -- | `dict` | Anthropic tool schema |
| `execute` | `**kwargs` | `ToolResult` | Execute with exception wrapping |

### `ToolParameter`

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `name` | `str` | -- | Parameter name |
| `param_type` | `ParameterType` | -- | JSON Schema type |
| `description` | `str` | -- | Human-readable description |
| `required` | `bool` | `True` | Whether the parameter is required |
| `enum` | `list[str]` | `None` | Allowed values |
| `default` | `Any` | `None` | Default value |
| `items_type` | `ParameterType` | `None` | Array item type |

### `ToolRegistry`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `register` | `tool: Tool` | `None` | Add a tool to the registry |
| `get` | `name: str` | `Tool` | Look up a tool by name |
| `list_tools` | `category: str` | `list[Tool]` | List all or category-filtered tools |
| `to_openai_format` | `category: str` | `list[dict]` | All tools in OpenAI format |
| `to_anthropic_format` | `category: str` | `list[dict]` | All tools in Anthropic format |
| `execute` | `tool_name: str, **kwargs` | `ToolResult` | Execute by name |

### `@tool` Decorator

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | `str` | func name | Tool name override |
| `description` | `str` | docstring | Tool description override |
| `category` | `str` | `None` | Tool category |
| `registry` | `ToolRegistry` | `None` | Auto-register to registry |

### `ParameterType` (Enum)

Values: `STRING`, `INTEGER`, `NUMBER`, `BOOLEAN`, `ARRAY`, `OBJECT`.
Maps to JSON Schema type strings.

## Built-in Tools

| Factory | Name | Description |
|---------|------|-------------|
| `create_calculator_tool()` | `calculator` | Safe math evaluation via AST parsing (no `eval()`) |
| `create_datetime_tool()` | `get_datetime` | Current datetime with strftime format |

## Dependencies

- **Internal**: None (standalone framework)
- **External**: stdlib (`inspect`, `json`, `ast`, `operator`, `functools`, `dataclasses`, `enum`, `datetime`)

## Constraints

- Calculator uses `ast.parse(mode="eval")` -- only arithmetic operators allowed, no function calls.
- `Tool.execute()` wraps all exceptions in `ToolResult(success=False)`.
- Python type-to-ParameterType mapping falls back to STRING for unknown types.
- Zero-mock: real execution only, `NotImplementedError` for unimplemented paths.

## Error Handling

- `ToolRegistry.execute()` returns error ToolResult for unknown tools (no exception raised).
- `Tool.execute()` catches all exceptions, returning `ToolResult(success=False, error=str(e))`.
- `ValueError` raised by calculator for unsupported AST node types.
- All errors logged before propagation.
