# Codomyrmex Agents — src/codomyrmex/validation

## Signposting
- **Parent**: [codomyrmex](../AGENTS.md)
- **Self**: [Validation Agents](AGENTS.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [Functional Spec](SPEC.md)
    - [Human Readme](README.md)

**Version**: v0.1.0 | **Status**: Proposed | **Last Updated**: December 2025

## Purpose

Validation module providing unified input validation framework with support for JSON Schema, Pydantic models, and custom validators for the Codomyrmex platform. This module consolidates validation logic currently scattered across modules.

The validation module serves as the validation layer, providing schema-agnostic validation interfaces with support for multiple validation libraries.

## Module Overview

### Key Capabilities
- **Schema Validation**: Validate data against JSON Schema
- **Model Validation**: Validate against Pydantic models
- **Custom Validators**: Register and use custom validation functions
- **Error Reporting**: Structured validation error messages
- **Nested Validation**: Support for complex nested structures

### Key Features
- Schema-agnostic validation interface
- Support for multiple validation libraries
- Structured error messages
- Nested validation support
- Custom validator registration

## Function Signatures

### Core Functions

```python
def validate(data: Any, schema: Any, validator_type: str = "json_schema") -> ValidationResult
```

Validate data against a schema using the specified validator type.

**Parameters:**
- `data` (Any): Data to validate
- `schema` (Any): Validation schema (JSON Schema dict, Pydantic model, or custom schema)
- `validator_type` (str): Type of validator to use ("json_schema", "pydantic", "custom"). Defaults to "json_schema"

**Returns:** `ValidationResult` - Validation result with `is_valid` boolean, `errors` list, and `warnings` list

**Raises:**
- `ValidationError`: If validation process fails

```python
def is_valid(data: Any, schema: Any, validator_type: str = "json_schema") -> bool
```

Check if data is valid against a schema.

**Parameters:**
- `data` (Any): Data to validate
- `schema` (Any): Validation schema
- `validator_type` (str): Type of validator to use. Defaults to "json_schema"

**Returns:** `bool` - True if valid, False otherwise

```python
def get_errors(data: Any, schema: Any, validator_type: str = "json_schema") -> list[ValidationError]
```

Get validation errors for data.

**Parameters:**
- `data` (Any): Data to validate
- `schema` (Any): Validation schema
- `validator_type` (str): Type of validator to use. Defaults to "json_schema"

**Returns:** `list[ValidationError]` - List of validation errors

### Validator Class

```python
class Validator:
    def __init__(self, validator_type: str = "json_schema") -> None
```

Base validator interface supporting multiple validation backends.

**Parameters:**
- `validator_type` (str): Type of validator ("json_schema", "pydantic", "custom"). Defaults to "json_schema"

**Methods:**

```python
def validate(self, data: Any, schema: Any) -> ValidationResult
```

Validate data against a schema using the configured validator type.

**Parameters:**
- `data` (Any): Data to validate
- `schema` (Any): Validation schema

**Returns:** `ValidationResult` - Validation result with status and errors

### ValidationManager Class

```python
class ValidationManager:
    def __init__(self) -> None
```

Manager for validation operations and custom validator registration.

**Methods:**

```python
def register_validator(self, name: str, validator: Callable) -> None
```

Register a custom validator function.

**Parameters:**
- `name` (str): Validator name
- `validator` (Callable): Validator function that takes (data, schema) and returns ValidationResult or bool

```python
def get_validator(self, name: str) -> Optional[Callable]
```

Get a registered validator.

**Parameters:**
- `name` (str): Validator name

**Returns:** `Optional[Callable]` - Validator function if found, None otherwise

```python
def validate(self, data: Any, schema: Any, validator_type: str = "json_schema") -> ValidationResult
```

Validate data against a schema using the specified validator type.

**Parameters:**
- `data` (Any): Data to validate
- `schema` (Any): Validation schema
- `validator_type` (str): Type of validator to use. Defaults to "json_schema"

**Returns:** `ValidationResult` - Validation result

### Validation Result

```python
class ValidationResult:
    is_valid: bool
    errors: list[ValidationError]
    warnings: list[ValidationWarning]
```

Validation result data structure.

```python
class ValidationError:
    field: str
    message: str
    code: str
    path: list[str]
```

Validation error data structure.

## Active Components

### Core Implementation
- `__init__.py` – Module initialization and public API exports
- `validator.py` – Base validator interface
- `validation_manager.py` – Validation manager
- `validators/` – Validator implementations
  - `json_schema_validator.py` – JSON Schema validator
  - `pydantic_validator.py` – Pydantic validator
  - `custom_validator.py` – Custom validator support

### Documentation
- `README.md` – Module usage and overview
- `AGENTS.md` – This file: agent documentation
- `SPEC.md` – Functional specification

## Operating Contracts

### Universal Validation Protocols

All validation operations within the Codomyrmex platform must:

1. **Error Reporting** - Provide clear, actionable error messages
2. **Schema Validation** - Validate schemas before use
3. **Nested Validation** - Support nested data structures
4. **Performance** - Optimize validation for common cases
5. **Type Safety** - Preserve type information where possible

### Integration Guidelines

When integrating with other modules:

1. **Use Config Management** - Integrate with config_management for config validation
2. **API Integration** - Support API module for request/response validation
3. **Document Validation** - Support documents module for document schema validation
4. **Error Recovery** - Provide clear error messages for validation failures

## Navigation Links

- **Human Documentation**: [README.md](README.md)
- **Functional Specification**: [SPEC.md](SPEC.md)

### Module Documentation
- **Module Overview**: [README.md](README.md) - Complete module documentation

### Platform Navigation
- **Parent Directory**: [codomyrmex](../README.md) - Package overview
- **Project Root**: [README](../../../README.md) - Main project documentation
- **Related Modules**:
    - [config_management](../config_management/AGENTS.md) - Configuration management
    - [api](../api/AGENTS.md) - API framework

