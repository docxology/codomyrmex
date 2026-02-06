# Personal AI Infrastructure — Validation Module

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The Validation module provides PAI integration for data and schema validation.

## PAI Capabilities

### Schema Validation

Validate data against schemas:

```python
from codomyrmex.validation import validate_schema

schema = {
    "type": "object",
    "properties": {"name": {"type": "string"}}
}

result = validate_schema(data, schema)
if not result.valid:
    print(result.errors)
```

### Type Validation

Validate types:

```python
from codomyrmex.validation import validate_type

result = validate_type(value, expected_type=int)
```

## PAI Integration Points

| Component | PAI Use Case |
|-----------|-------------|
| `validate_schema` | Schema validation |
| `validate_type` | Type validation |
| `Validator` | Custom validators |

## Navigation

- [README](README.md) | [AGENTS](AGENTS.md) | [SPEC](SPEC.md)
