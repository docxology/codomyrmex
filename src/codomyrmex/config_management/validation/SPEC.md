# Configuration Validation -- Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Provides comprehensive configuration validation with schema-based type checking, constraint enforcement (min, max, length, pattern, enum, custom), required field detection, nested schema support, custom validator registration, and detailed issue reporting with actionable suggestions.

## Architecture

Schema-driven validation engine. `ConfigValidator` validates a configuration dictionary against a `ConfigSchema` tree, running built-in constraint checks and user-registered custom validators. Issues are classified by severity (`ERROR`, `WARNING`, `INFO`) and returned in a structured `ValidationResult`.

## Key Classes

### `ConfigValidator`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `__init__` | `schema: dict[str, ConfigSchema] \| None` | `None` | Initializes with optional schema |
| `validate` | `config: dict[str, Any]` | `ValidationResult` | Validates config against schema and custom validators |
| `validate_required_fields` | `config, required: list[str]` | `list[str]` | Returns names of missing required fields |
| `validate_types` | `config, schema: dict[str, Any]` | `list[ValidationIssue]` | Checks value types against a type map |
| `validate_values` | `config, constraints: dict[str, dict]` | `list[ValidationIssue]` | Validates values against constraint rules |
| `add_custom_validator` | `name: str, validator: Callable` | `None` | Registers a named custom validator |

### `ConfigSchema` (Dataclass)

Fields: `type: str`, `required: bool`, `default: Any`, `description: str`, `constraints: dict`, `nested_schema: dict[str, ConfigSchema] | None`

### `ValidationResult` (Dataclass)

Fields: `is_valid: bool`, `issues`, `warnings`, `errors`; method `add_issue(issue)` auto-classifies by severity.

### `ValidationIssue` (Dataclass)

Fields: `field_path`, `message`, `severity: ValidationSeverity`, `suggestion`, `actual_value`, `expected_value`

### `ValidationSeverity` (Enum)

Values: `ERROR`, `WARNING`, `INFO`

### Predefined Schema Factories

| Function | Returns | Description |
|----------|---------|-------------|
| `get_logging_config_schema` | `dict[str, ConfigSchema]` | Schema for logging config (level, format, file, max_file_size) |
| `get_database_config_schema` | `dict[str, ConfigSchema]` | Schema for database config (host, port, database, SSL, connection pool) |
| `get_ai_model_config_schema` | `dict[str, ConfigSchema]` | Schema for AI model config (provider, model, temperature, retry) |

## Dependencies

- **Internal**: `codomyrmex.logging_monitoring.core.logger_config`
- **External**: `re` (stdlib)

## Constraints

- Supported types: `str`, `int`, `float`, `bool`, `list`, `dict`, `any`.
- Supported constraints: `min`, `max`, `min_length`, `max_length`, `pattern` (regex), `enum` (list of allowed values), `custom` (callable).
- Unknown fields in config trigger `WARNING` severity, not errors.
- Custom validators may return `ValidationResult` or `list[ValidationIssue]`.
- Zero-mock: real validation only, `NotImplementedError` for unimplemented paths.

## Error Handling

- Custom validator failures are caught, logged via `logger.error`, and added as `ERROR` severity issues.
- All errors are logged before propagation.
