# Codomyrmex Agents — src/codomyrmex/validation

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose

The Validation module provides a unified input validation framework for Codomyrmex with support for JSON Schema validation, Pydantic model validation, and custom validators. It enables consistent data validation across the codebase with structured error reporting, contextual cross-field validation, and comprehensive examples validation for quality assurance.

## Active Components

### Core Validation

- `validator.py` - Base validator implementation with multiple backends
  - Key Classes: `Validator`, `ValidationResult`, `ValidationError`, `ValidationWarning`
  - Key Functions: `validate()`, `is_valid()`, `get_errors()`

### Validation Management

- `validation_manager.py` - Validator registration and management
  - Key Classes: `ValidationManager`
  - Key Functions: `register_validator()`, `get_validator()`, `validate()`

### Contextual Validation

- `contextual.py` - Cross-field validation rules
  - Key Classes: `ContextualValidator`, `ValidationIssue`

### Examples Validation

- `examples_validator.py` - Comprehensive validation for Codomyrmex examples and modules
  - Key Classes: `ExamplesValidator`, `ModuleValidationResult`, `ValidationIssue`
  - Key Enums: `ValidationSeverity`, `ValidationType`

## Key Classes and Functions

| Class/Function | Module | Purpose |
| :--- | :--- | :--- |
| `Validator` | validator | Base validator with JSON Schema and Pydantic support |
| `ValidationResult` | validator | Validation result with is_valid, errors, and warnings |
| `ValidationError` | validator | Validation error with field, message, code, and path |
| `ValidationWarning` | validator | Validation warning dataclass |
| `ValidationManager` | validation_manager | Manager for registering custom validators |
| `ContextualValidator` | contextual | Cross-field validation rule execution |
| `ValidationIssue` | contextual | Issue dataclass with field, message, and severity |
| `ExamplesValidator` | examples_validator | Validator for Codomyrmex examples |
| `ModuleValidationResult` | examples_validator | Result of validating a single module |
| `ValidationSeverity` | examples_validator | Enum: CRITICAL, ERROR, WARNING, INFO |
| `ValidationType` | examples_validator | Enum: EXECUTION, CONFIGURATION, DOCUMENTATION, etc. |
| `validate()` | validator | Validate data against a schema |
| `is_valid()` | validator | Check if data is valid against a schema |
| `get_errors()` | validator | Get validation errors for data |
| `register_validator()` | ValidationManager | Register a custom validator function |
| `add_rule()` | ContextualValidator | Add a custom validation rule |
| `validate_all()` | ExamplesValidator | Run all validation checks on modules |
| `_validate_json_schema()` | Validator | Validate using JSON Schema |
| `_validate_pydantic()` | Validator | Validate using Pydantic model |
| `_validate_custom()` | Validator | Validate using custom validator function |
| `_basic_validation()` | Validator | Basic validation without external libraries |

## Operating Contracts

1. **Logging**: All validation operations use `logging_monitoring` for structured logging
2. **JSON Schema**: Uses `jsonschema` library with fallback to basic validation if unavailable
3. **Pydantic Support**: Integrates with Pydantic models for type-safe validation
4. **Error Structure**: ValidationError includes field, message, code, and path for detailed reporting
5. **Validator Types**: Supports "json_schema", "pydantic", and "custom" validator types
6. **Custom Validators**: Custom validators return bool or ValidationResult
7. **Examples Validation**: Parallel execution with configurable job count

## Validation Types

| Type | Purpose |
| :--- | :--- |
| EXECUTION | Validate script execution (dry run) |
| CONFIGURATION | Validate YAML/JSON configuration files |
| DOCUMENTATION | Validate README.md and docstrings |
| TEST_REFERENCES | Validate test file references |
| OUTPUT_FILES | Validate expected output files |

## Integration Points

- **logging_monitoring** - All validation functions log via centralized logger
- **exceptions** - Uses `CodomyrmexError` as base exception class
- **utils/cli_helpers** - CLI utilities for output formatting
- **All modules** - Provides validation for data inputs across the codebase

## Signposting

### Document Hierarchy

- **Self**: [AGENTS.md](AGENTS.md)
- **Parent**: [src/codomyrmex/AGENTS.md](../AGENTS.md)
- **Project Root**: [../../../AGENTS.md](../../../AGENTS.md)

### Sibling Modules

| Module | AGENTS.md | Purpose |
| :--- | :--- | :--- |
| logging_monitoring | [../logging_monitoring/AGENTS.md](../logging_monitoring/AGENTS.md) | Logging infrastructure |
| config_management | [../config_management/AGENTS.md](../config_management/AGENTS.md) | Configuration management |
| tests | [../tests/AGENTS.md](../tests/AGENTS.md) | Test framework |
| security | [../security/AGENTS.md](../security/AGENTS.md) | Security utilities |

### Related Documentation

- [README.md](README.md) - User documentation
- [API_SPECIFICATION.md](API_SPECIFICATION.md) - API documentation
- [SPEC.md](SPEC.md) - Functional specification
