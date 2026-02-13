# Tool Use API Specification

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The `tool_use` module provides infrastructure for registering, validating, invoking, and composing tools in a pipeline. It includes JSON-schema-like validation, a central registry with decorator support, and a chain abstraction for sequential multi-tool execution.

## Core API

### ValidationResult (dataclass)

Result of a validation operation.

| Field | Type | Default | Description |
|:------|:-----|:--------|:------------|
| `valid` | `bool` | `True` | Whether the data passed all validation checks |
| `errors` | `list[str]` | `[]` | List of human-readable error descriptions |

**Methods:**

| Method | Signature | Returns | Description |
|:-------|:----------|:--------|:------------|
| `merge` | `(other: ValidationResult) -> ValidationResult` | `ValidationResult` | Merge another result; combined valid and errors |
| `to_dict` | `() -> dict[str, Any]` | `dict` | Convert to plain dictionary |

### validate_input

```python
def validate_input(data: Any, schema: dict[str, Any]) -> ValidationResult
```

Validate tool input data against a JSON-schema-like specification.

**Parameters:**

| Parameter | Type | Required | Description |
|:----------|:-----|:---------|:------------|
| `data` | `Any` | Yes | The input data to validate (typically a dict) |
| `schema` | `dict[str, Any]` | Yes | JSON-schema-like dict describing expected structure |

**Supported schema keywords:** `type`, `required`, `properties`, `items`, `enum`, `minimum`, `maximum`, `minLength`, `maxLength`, `minItems`, `maxItems`, `additionalProperties`.

**Returns:** `ValidationResult` with `valid=True` if data conforms, or `valid=False` with error messages.

### validate_output

```python
def validate_output(data: Any, schema: dict[str, Any]) -> ValidationResult
```

Validate tool output data against a JSON-schema-like specification. Uses the same validation logic as `validate_input`, separated for clarity in error reporting and independent extensibility.

**Parameters:** Same as `validate_input`.

**Returns:** `ValidationResult`.

---

### ToolEntry (dataclass)

A registered tool entry in the registry.

| Field | Type | Default | Description |
|:------|:-----|:--------|:------------|
| `name` | `str` | (required) | Unique identifier for the tool |
| `description` | `str` | (required) | Human-readable description |
| `handler` | `Callable[..., Any]` | (required) | The callable that executes tool logic |
| `input_schema` | `dict[str, Any]` | `{}` | JSON-schema-like input specification |
| `output_schema` | `dict[str, Any]` | `{}` | JSON-schema-like output specification |
| `tags` | `list[str]` | `[]` | Categorization tags for filtering |

**Methods:**

| Method | Signature | Returns | Description |
|:-------|:----------|:--------|:------------|
| `to_tool_definition` | `(module: str = "tool_use") -> ToolDefinition` | `ToolDefinition` | Convert to shared ToolDefinition schema type |
| `to_dict` | `() -> dict[str, Any]` | `dict` | Convert to plain dictionary (excludes handler) |

### ToolRegistry

Central registry for managing available tools. Supports registration, lookup, search by tags/name, and invocation with optional input/output validation.

**Constructor:**

```python
ToolRegistry()
```

**Methods:**

| Method | Signature | Returns | Description |
|:-------|:----------|:--------|:------------|
| `register` | `(entry: ToolEntry) -> None` | `None` | Register a tool. Raises `ValueError` if name exists |
| `unregister` | `(name: str) -> bool` | `bool` | Remove by name. Returns True if found |
| `get` | `(name: str) -> ToolEntry \| None` | `ToolEntry \| None` | Retrieve by exact name |
| `list` | `() -> list[ToolEntry]` | `list[ToolEntry]` | All entries sorted by name |
| `list_names` | `() -> list[str]` | `list[str]` | All tool names sorted |
| `search` | `(*, name_contains, tags, match_all_tags) -> list[ToolEntry]` | `list[ToolEntry]` | Search by name substring and/or tags |
| `invoke` | `(name, input_data, *, validate=True) -> Result` | `Result` | Look up and invoke a tool with validation |

**`search()` parameters:**

| Parameter | Type | Required | Description |
|:----------|:-----|:---------|:------------|
| `name_contains` | `str \| None` | No | Case-insensitive name substring |
| `tags` | `list[str] \| None` | No | Tags to filter by |
| `match_all_tags` | `bool` | No | If True, all tags must match (default False = any) |

**`invoke()` parameters:**

| Parameter | Type | Required | Description |
|:----------|:-----|:---------|:------------|
| `name` | `str` | Yes | Registered tool name |
| `input_data` | `Any` | No | Data passed to tool handler |
| `validate` | `bool` | No | Validate input/output (default True) |

**Returns:** `Result` object with status, data, message, errors, and duration_ms.

**Dunder methods:** `__len__`, `__contains__`, `__repr__`.

### tool (Decorator)

```python
@tool(
    name: str,
    description: str = "",
    input_schema: dict | None = None,
    output_schema: dict | None = None,
    tags: list[str] | None = None,
    registry: ToolRegistry | None = None,
)
```

Marks a function as a tool and optionally registers it. The decorated function retains a `tool_entry` attribute containing the `ToolEntry`, usable for deferred registration.

**Parameters:**

| Parameter | Type | Required | Description |
|:----------|:-----|:---------|:------------|
| `name` | `str` | Yes | Unique tool name |
| `description` | `str` | No | Human-readable description |
| `input_schema` | `dict \| None` | No | JSON-schema-like input spec |
| `output_schema` | `dict \| None` | No | JSON-schema-like output spec |
| `tags` | `list[str] \| None` | No | Categorization tags |
| `registry` | `ToolRegistry \| None` | No | If provided, auto-registers the tool |

---

### ChainStep (dataclass)

A single step in a tool chain.

| Field | Type | Default | Description |
|:------|:-----|:--------|:------------|
| `tool_name` | `str` | (required) | Name of the tool to invoke |
| `input_mapping` | `dict[str, str]` | `{}` | Maps tool input keys to context keys (supports dot-notation) |
| `output_key` | `str` | `""` | Key to store output under in context. Empty = merge into context |

**Methods:**

| Method | Signature | Returns | Description |
|:-------|:----------|:--------|:------------|
| `to_dict` | `() -> dict[str, Any]` | `dict` | Convert to plain dictionary |

### ChainResult (dataclass)

Result of executing an entire tool chain.

| Field | Type | Default | Description |
|:------|:-----|:--------|:------------|
| `success` | `bool` | `True` | Whether all steps completed successfully |
| `context` | `dict[str, Any]` | `{}` | Accumulated context after all steps |
| `step_results` | `list[Result]` | `[]` | Per-step Result objects in execution order |
| `errors` | `list[str]` | `[]` | Aggregated errors from all steps |
| `duration_ms` | `float` | `0.0` | Total wall-clock time for the chain |

**Methods:**

| Method | Signature | Returns | Description |
|:-------|:----------|:--------|:------------|
| `to_dict` | `() -> dict[str, Any]` | `dict` | Convert to plain dictionary |

### ToolChain

A pipeline of tools that execute sequentially. Outputs from earlier steps are available to later steps via the accumulated context.

**Constructor:**

```python
ToolChain(registry: ToolRegistry)
```

**Methods:**

| Method | Signature | Returns | Description |
|:-------|:----------|:--------|:------------|
| `add_step` | `(step: ChainStep) -> ToolChain` | `ToolChain` | Append step (fluent API) |
| `validate` | `() -> ValidationResult` | `ValidationResult` | Validate all referenced tools exist |
| `execute` | `(initial_input, *, stop_on_failure, validate_tools) -> ChainResult` | `ChainResult` | Execute all steps sequentially |
| `clear` | `() -> None` | `None` | Remove all steps |

**`execute()` parameters:**

| Parameter | Type | Default | Description |
|:----------|:-----|:--------|:------------|
| `initial_input` | `dict[str, Any] \| None` | `None` | Starting context for the first step |
| `stop_on_failure` | `bool` | `True` | Stop chain on first tool failure |
| `validate_tools` | `bool` | `True` | Pre-validate all referenced tools exist |

**Properties:** `steps` (read-only copy of step list).

**Dunder methods:** `__len__`, `__repr__`.

## Error Handling

| Exception | Raised When |
|:----------|:------------|
| `ValueError` | Registering a tool with a duplicate name |

Validation failures return `ValidationResult` with `valid=False` rather than raising exceptions. Invocation failures return `Result` with `status=FAILURE`.

## Integration Points

- `codomyrmex.schemas` -- Uses `Result`, `ResultStatus`, `ToolDefinition` types
- `model_context_protocol` -- ToolEntry converts to ToolDefinition for MCP exposure
- `agents` -- Agent frameworks use ToolRegistry for tool discovery and invocation

## Navigation

- **Human Documentation**: [README.md](README.md)
- **MCP Tools**: [MCP_TOOL_SPECIFICATION.md](MCP_TOOL_SPECIFICATION.md)
- **PAI Integration**: [PAI.md](PAI.md)
- **Parent Directory**: [codomyrmex](../README.md)
