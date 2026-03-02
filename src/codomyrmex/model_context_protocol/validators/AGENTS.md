# Codomyrmex Agents — src/codomyrmex/model_context_protocol/validators

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Provides pure-Python validators for MCP protocol elements: JSON Schema validation, tool call argument checking, JSON-RPC message compliance, and MCP specification file auditing. All validators return structured `ValidationResult` objects with errors and warnings.

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `__init__.py` | `SchemaValidator` | Recursive JSON Schema validator supporting object, array, string, integer, number, and boolean types |
| `__init__.py` | `ToolCallValidator` | Validates tool calls against registered input schemas; checks tool existence and argument conformance |
| `__init__.py` | `MessageValidator` | Validates JSON-RPC 2.0 requests and responses: version, method, id, params, result/error exclusivity |
| `__init__.py` | `SpecificationValidator` | Audits `MCP_TOOL_SPECIFICATION.md` files for required sections (description, invocation name, input/output schema), JSON examples, and security considerations |
| `__init__.py` | `ValidationResult` | Dataclass with `valid: bool`, `errors: list[str]`, `warnings: list[str]`; supports `bool()` truthiness |
| `__init__.py` | `validate_tool_call()` | Convenience function wrapping `ToolCallValidator` |
| `__init__.py` | `validate_message()` | Convenience function wrapping `MessageValidator` for request or response validation |

## Operating Contracts

- `SchemaValidator` recursively validates nested objects and arrays against their property/item schemas.
- `MessageValidator.validate_response()` enforces JSON-RPC 2.0 rule: a response must have either `result` or `error`, never both.
- `SpecificationValidator` produces warnings (not errors) for missing sections, allowing partial specs to pass validation.
- `ToolCallValidator.validate_result()` checks that failure statuses have an error field and flags data-on-failure as a warning.
- All validators are stateless; no side effects.
- Errors must be logged via `logging_monitoring` before re-raising.

## Integration Points

- **Depends on**: `codomyrmex.logging_monitoring` (structured logging)
- **Used by**: Protocol compliance checks, documentation quality audits, test harnesses

## Navigation

- **Parent**: [model_context_protocol](../README.md)
- **Root**: [Root](../../../../README.md)
