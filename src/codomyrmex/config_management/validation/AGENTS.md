# Codomyrmex Agents -- src/codomyrmex/config_management/validation

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Provides comprehensive configuration validation with schema-based type checking, constraint enforcement, required field verification, custom validators, and detailed error reporting with actionable suggestions.

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `config_validator.py` | `ConfigValidator` | Main validator with schema support and custom validator registration |
| `config_validator.py` | `ConfigValidator.validate` | Validates a config dict against a schema, returning `ValidationResult` |
| `config_validator.py` | `ConfigValidator.validate_required_fields` | Checks that required fields are present and non-None |
| `config_validator.py` | `ConfigValidator.validate_types` | Validates value types against a type schema |
| `config_validator.py` | `ConfigValidator.validate_values` | Validates values against constraint rules |
| `config_validator.py` | `ConfigValidator.add_custom_validator` | Registers a callable custom validation function |
| `config_validator.py` | `ConfigSchema` | Dataclass defining field type, required flag, default, constraints, and nested schemas |
| `config_validator.py` | `ValidationResult` | Dataclass holding validation status, issues, warnings, and errors |
| `config_validator.py` | `ValidationIssue` | Dataclass for a single issue with field path, severity, and suggestion |
| `config_validator.py` | `ValidationSeverity` | Enum: `ERROR`, `WARNING`, `INFO` |
| `config_validator.py` | `get_logging_config_schema` | Predefined schema for logging configuration |
| `config_validator.py` | `get_database_config_schema` | Predefined schema for database configuration |
| `config_validator.py` | `get_ai_model_config_schema` | Predefined schema for AI model configuration |
| `config_validator.py` | `validate_config_schema` | Convenience function returning `(is_valid, error_messages)` tuple |

## Operating Contracts

- Supported constraint types: `min`, `max`, `min_length`, `max_length`, `pattern`, `enum`, `custom`.
- Type checking supports: `str`, `int`, `float`, `bool`, `list`, `dict`, `any`.
- Unknown fields in a config are reported as `WARNING` severity, not errors.
- Custom validators can return either `ValidationResult` or `list[ValidationIssue]`.
- Errors must be logged via `logging_monitoring` before re-raising.

## Integration Points

- **Depends on**: `codomyrmex.logging_monitoring.core.logger_config`
- **Used by**: Config management MCP tools (`validate_config`), deployment pipelines, module initialization

## Navigation

- **Parent**: [../AGENTS.md](../AGENTS.md)
- **Root**: [../../../../README.md](../../../../README.md)
