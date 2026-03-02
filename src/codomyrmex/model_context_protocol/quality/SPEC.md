# Quality — Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Argument validation, tool taxonomy classification, and testing framework for MCP tools. Ensures tool arguments conform to their JSON Schema before execution, classifies tools into semantic categories for access control and documentation, and provides test harnesses for tools, servers, and integration scenarios.

## Architecture

Three independent sub-modules behind a unified `__init__.py`:

- **validation**: Pure-Python JSON Schema validation with optional `jsonschema` library acceleration and lightweight type coercion.
- **taxonomy**: Regex-based auto-classification of tool names into `ToolCategory` enum values.
- **testing**: Layered test harnesses: `ToolTester` (unit), `ServerTester` (protocol), `IntegrationTester` (end-to-end scenarios).

## Key Classes

### `validate_tool_arguments()`

| Parameter | Type | Description |
|-----------|------|-------------|
| `tool_name` | `str` | For logging and error messages only |
| `arguments` | `dict[str, Any] | None` | Raw arguments from caller |
| `schema` | `dict[str, Any]` | Tool schema with `inputSchema` key or bare JSON Schema |
| `coerce` | `bool` (default `True`) | Enable string-to-type coercion |

Returns `ValidationResult(valid, errors, coerced_args)`.

### `_generate_schema_from_func()`

| Parameter | Type | Description |
|-----------|------|-------------|
| `func` | `Callable` | Function to introspect |

Returns a JSON Schema `{"type": "object", "properties": {...}, "required": [...]}` derived from function signature and type annotations. Maps `str`, `int`, `float`, `bool`, `list`, `dict` to their JSON Schema equivalents.

### `ToolCategory` (enum)

| Value | Meaning |
|-------|---------|
| `ANALYSIS` | Read-only inspection (code review, static analysis) |
| `GENERATION` | Creates new content (diagrams, docs, charts) |
| `EXECUTION` | Runs code or commands (side-effects) |
| `QUERY` | Retrieves data without side-effects |
| `MUTATION` | Modifies persistent state (files, git, notes) |

### `ToolTester`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `test_tool` | `tool_name: str, test_cases: list[dict]` | `TestSuite` | Run test cases against a registry tool; checks expected output or just no-error |

### `ServerTester`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `test_initialize` | — | `TestResult` | Verify the JSON-RPC `initialize` handshake returns `protocolVersion` and `capabilities` |
| `test_tools_list` | — | `TestResult` | Verify `tools/list` returns a `tools` array |
| `test_tool_call` | `tool_name: str, arguments: dict` | `TestResult` | Call a specific tool and check for `content` in response |
| `run_smoke_tests` | — | `TestSuite` | Run initialize + tools/list as a smoke suite |

### `IntegrationTester`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `add_scenario` | `name, steps, description` | `None` | Register a multi-step scenario |
| `run_scenario` | `scenario, server` | `TestSuite` | Execute steps sequentially with shared context and `$`-variable templating |
| `run_all` | `server` | `list[TestSuite]` | Run all registered scenarios |

## Dependencies

- **Internal**: `codomyrmex.logging_monitoring`
- **External**: `jsonschema` (optional, preferred for validation), standard library (`inspect`, `re`, `time`, `asyncio`)

## Constraints

- When `jsonschema` is not installed, the built-in validator handles `required`, `type`, `enum`, `minimum`/`maximum`, and `pattern` checks only.
- Type coercion is best-effort: failed coercion lets the downstream validation produce the error.
- Taxonomy rules are ordered; first regex match wins.
- Zero-mock: real data only, `NotImplementedError` for unimplemented paths.

## Error Handling

- `validate_tool_arguments` returns `ValidationResult(valid=False, errors=[...])` on failure; never raises.
- `ToolTester` and `ServerTester` catch all exceptions per test case, recording them in `TestResult.error`.
- All errors logged before propagation.
