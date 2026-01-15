# Validation Module

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Overview

The Validation module provides a unified input validation framework for Codomyrmex, supporting JSON Schema validation, Pydantic models, and custom validators.

## Validator Types

| Type | Description |
|------|-------------|
| `json_schema` | JSON Schema draft-07 validation (default) |
| `pydantic` | Pydantic model validation |
| `custom` | Custom validation functions |

## Key Features

- **JSON Schema**: Full JSON Schema draft-07 support
- **Pydantic Integration**: Validate against Pydantic models
- **Custom Validators**: Register custom validation logic
- **Detailed Errors**: Rich error messages with field paths
- **Warnings**: Non-fatal validation warnings

## Quick Start

```python
from codomyrmex.validation import (
    validate, is_valid, get_errors,
    Validator, ValidationManager,
    ValidationResult, ValidationError,
)

# JSON Schema validation
schema = {
    "type": "object",
    "properties": {
        "name": {"type": "string", "minLength": 1},
        "age": {"type": "integer", "minimum": 0},
        "email": {"type": "string", "format": "email"},
    },
    "required": ["name", "email"]
}

data = {"name": "Alice", "age": 30, "email": "alice@example.com"}

# Quick validation check
if is_valid(data, schema):
    print("Valid!")

# Get validation result with details
result = validate(data, schema)
if result.is_valid:
    print("Data is valid")
else:
    for error in result.errors:
        print(f"Error in {error.field}: {error.message}")

# Get only errors
errors = get_errors(data, schema)
for error in errors:
    print(f"{error.field}: {error.message} (code: {error.code})")

# Using the Validator class
validator = Validator(validator_type="json_schema")
result = validator.validate(data, schema)
```

## Core Classes

| Class | Description |
|-------|-------------|
| `Validator` | Core validation with type selection |
| `ValidationManager` | Manage multiple validators |
| `ValidationResult` | Result with is_valid, errors, warnings |
| `ValidationError` | Error with message, field, code |
| `ValidationWarning` | Warning for non-fatal issues |

## Convenience Functions

| Function | Description |
|----------|-------------|
| `validate(data, schema, validator_type)` | Full validation result |
| `is_valid(data, schema, validator_type)` | Quick boolean check |
| `get_errors(data, schema, validator_type)` | Get list of errors only |

## Exceptions

| Exception | Description |
|-----------|-------------|
| `ValidationError` | Validation failed with details |

## Navigation

- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: [README](../../../README.md)
