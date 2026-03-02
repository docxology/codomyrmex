# Agent Guidelines - Validation

**Version**: v1.0.5 | **Status**: Active | **Last Updated**: March 2026

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

## MCP Tools Available

All tools are auto-discovered via `@mcp_tool` decorators and exposed through the MCP bridge.

| Tool | Description | Trust Level |
|------|-------------|-------------|
| `validate_schema` | Validate data against a JSON Schema | Safe |
| `validate_config` | Validate a configuration dictionary against common patterns | Safe |
| `validation_summary` | Get a summary of validation operations performed in this session | Safe |

## PAI Agent Role Access Matrix

| PAI Agent | Access Level | Primary Capabilities | Trust Level |
|-----------|-------------|---------------------|-------------|
| **Engineer** | Full | `validate_schema`, `validate_config`, `validation_summary`; complete validation pipeline | TRUSTED |
| **Architect** | Read + Design | `validate_schema`; schema design review, data contract validation | OBSERVED |
| **QATester** | Validation | `validate_schema`, `validate_config`, `validation_summary`; full VERIFY-phase validation | OBSERVED |

### Engineer Agent
**Use Cases**: Schema validation at system boundaries during BUILD, config validation before EXECUTE, generating validation summaries.

### Architect Agent
**Use Cases**: Reviewing data schemas, validating API contracts, confirming data shapes match design.

### QATester Agent
**Use Cases**: Running full validation suite during VERIFY, generating compliance reports, confirming schema correctness.

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)
