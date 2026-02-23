# Agent Guidelines - Validation

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Module Overview

Data validation, schema checking, and input sanitization.

## Key Classes

- **Validator** — General validation
- **SchemaValidator** — JSON Schema validation
- **EmailValidator** — Email format validation
- **URLValidator** — URL format validation

## Agent Instructions

1. **Validate early** — Check at API boundaries
2. **Return all errors** — Don't stop at first error
3. **Use schemas** — Define validation schemas
4. **Custom messages** — User-friendly error messages
5. **Whitelist** — Prefer whitelist over blacklist

## Common Patterns

```python
from codomyrmex.validation import (
    Validator, SchemaValidator, validate, ValidationError
)

# Simple validation
validator = Validator()
errors = validator.validate({
    "email": "user@example.com",
    "age": 25
}, rules={
    "email": ["required", "email"],
    "age": ["required", "min:18"]
})

if errors:
    raise ValidationError(errors)

# Schema validation
schema = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "count": {"type": "integer"}
    },
    "required": ["name"]
}
SchemaValidator.validate(data, schema)
```

## Testing Patterns

```python
# Verify validation
validator = Validator()
errors = validator.validate(
    {"email": "invalid"},
    rules={"email": ["email"]}
)
assert len(errors) > 0

# Verify valid input
errors = validator.validate(
    {"email": "test@test.com"},
    rules={"email": ["email"]}
)
assert len(errors) == 0
```

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)
