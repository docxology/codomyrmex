# Codomyrmex Agents -- src/codomyrmex/llm/tools

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Provides a tool-calling framework for LLMs with structured tool definitions,
a registry for managing available tools, automatic parameter extraction from
function signatures, and serialization to both OpenAI and Anthropic tool
formats. Includes a `@tool` decorator for declarative tool creation.

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `__init__.py` | `Tool` | Core tool dataclass with name, description, parameters, function, and category |
| `__init__.py` | `ToolRegistry` | Registry for managing, listing, and executing tools by name or category |
| `__init__.py` | `ToolParameter` | Parameter definition with JSON Schema type, description, required flag, and enum support |
| `__init__.py` | `ToolResult` | Execution result with success flag, output, error, and metadata |
| `__init__.py` | `ParameterType` | Enum mapping to JSON Schema types (STRING, INTEGER, NUMBER, BOOLEAN, ARRAY, OBJECT) |
| `__init__.py` | `tool` | Decorator that creates a `Tool` from a function's signature and docstring |
| `__init__.py` | `create_calculator_tool()` | Built-in safe calculator using AST-based evaluation (no `eval()`) |
| `__init__.py` | `create_datetime_tool()` | Built-in datetime tool with configurable strftime format |
| `__init__.py` | `DEFAULT_REGISTRY` | Global singleton tool registry |

## Operating Contracts

- `Tool.execute()` catches all exceptions and returns `ToolResult(success=False, error=...)`.
- The `@tool` decorator extracts parameters from function signatures and type hints automatically.
- `Tool.to_openai_format()` and `Tool.to_anthropic_format()` produce provider-specific tool schemas.
- The built-in calculator uses `ast.parse(mode="eval")` for safe expression evaluation -- never `eval()`.
- `ToolRegistry.execute()` returns an error `ToolResult` for unknown tool names (no exception).
- Errors must be logged via `logging_monitoring` before re-raising.

## Integration Points

- **Depends on**: stdlib `inspect`, `json`, `ast`, `functools`, `dataclasses`, `enum`
- **Used by**: `llm/providers/` (OpenAI, Anthropic), `agents/core`, MCP bridge tool dispatch

## Navigation

- **Parent**: [llm](../AGENTS.md)
- **Root**: [../../../../README.md](../../../../README.md)
