# Validators — Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Pure-Python validators for MCP protocol compliance: JSON Schema validation, tool call checking, JSON-RPC 2.0 message validation, and specification file auditing. No external dependencies beyond standard library.

## Architecture

Four validator classes, each stateless and returning `ValidationResult` with `valid`, `errors`, and `warnings` fields. Two convenience functions provide simplified access for common cases.

## Key Classes

### `SchemaValidator`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `validate` | `data: Any` | `ValidationResult` | Validate data against the stored JSON Schema; supports object, array, string, integer, number, boolean types |

Internal recursive methods:
- `_validate_object()` — checks required fields and validates each property against its sub-schema
- `_validate_array()` — validates each item against the `items` schema

### `ToolCallValidator`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `validate_call` | `tool_name: str, arguments: dict` | `ValidationResult` | Check tool exists in registered schemas; validate arguments |
| `validate_result` | `result: dict` | `ValidationResult` | Check result has `status`; enforce error on failure, warn on data-with-failure |

Constructor takes `tool_schemas: dict[str, dict[str, Any]]` mapping tool names to their input schemas.

### `MessageValidator`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `validate_request` | `message: dict` | `ValidationResult` | Check JSON-RPC version, method string, id type, params type |
| `validate_response` | `message: dict` | `ValidationResult` | Check version, id presence, result/error exclusivity, error structure (code + message) |

Constant: `JSONRPC_VERSION = "2.0"`

### `SpecificationValidator`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `validate_spec_file` | `content: str` | `ValidationResult` | Audit MCP spec file for required sections, JSON examples, and security considerations |

Required sections checked: `description`, `invocation name`, `input schema`, `output schema`.

### `ValidationResult`

| Field | Type | Description |
|-------|------|-------------|
| `valid` | `bool` | Whether validation passed |
| `errors` | `list[str]` | Hard errors that cause validation failure |
| `warnings` | `list[str]` | Advisory warnings that do not fail validation |

Supports `bool()` protocol: `bool(result)` returns `result.valid`.

### Convenience Functions

| Function | Parameters | Returns | Description |
|----------|-----------|---------|-------------|
| `validate_tool_call` | `tool_name, arguments, schemas` | `ValidationResult` | Wrapper around `ToolCallValidator.validate_call()` |
| `validate_message` | `message, message_type="request"` | `ValidationResult` | Wrapper around `MessageValidator` for request or response |

## Dependencies

- **Internal**: `codomyrmex.logging_monitoring`
- **External**: Standard library only (`json`, `re`, `dataclasses`)

## Constraints

- `SchemaValidator` does not support `$ref`, `oneOf`, `anyOf`, `allOf`, or conditional schemas; these require the `jsonschema` library (available in `quality.validation`).
- Integer validation explicitly excludes `bool` (Python `bool` is subclass of `int`).
- `SpecificationValidator` produces warnings only; `valid` is always `True`.
- Zero-mock: real data only, `NotImplementedError` for unimplemented paths.

## Error Handling

- Validators never raise; they return `ValidationResult` with errors/warnings.
- `ValidationResult.valid` is `False` only when `errors` is non-empty.
- All errors logged before propagation.
