# validation

## Signposting
- **Parent**: [codomyrmex](../README.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [Agent Guide](AGENTS.md)
    - [Functional Spec](SPEC.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Overview

Unified input validation framework with support for JSON Schema, Pydantic models, and custom validators. Provides structured error reporting, nested validation support, and a pluggable validator system for consolidating validation logic across the Codomyrmex ecosystem.

## Directory Contents
- `README.md` – File
- `SPEC.md` – File
- `__init__.py` – File
- `validation_manager.py` – File
- `validator.py` – File

## Navigation
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: [README](../../../README.md)

## Getting Started

To use this module in your project, import the necessary components:

```python
from codomyrmex.validation import validate, is_valid, ValidationError, Validator, ValidationManager

# Basic validation with JSON Schema
schema = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "age": {"type": "integer"}
    },
    "required": ["name"]
}

data = {"name": "Alice", "age": 30}
result = validate(data, schema)
if result.is_valid:
    print("Validation passed")
else:
    for error in result.errors:
        print(f"Error: {error.message}")

# Quick validation check
if is_valid(data, schema):
    print("Data is valid")

# Using ValidationManager for custom validators
manager = ValidationManager()
manager.register_validator("custom", lambda d, s: len(d) > 0)
result = manager.validate(data, schema, validator_type="custom")
```

