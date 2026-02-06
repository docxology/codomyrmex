# Validation Documentation

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Data and schema validation utilities.

## Key Features

- **Schema** — JSON Schema validation
- **Types** — Type validation
- **Rules** — Custom rules
- **Errors** — Descriptive errors

## Quick Start

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

## Directory Contents

| File | Description |
|------|-------------|
| `README.md` | This file |
| `SPEC.md` | Technical specification |

## Navigation

- **Source**: [src/codomyrmex/validation/](../../../src/codomyrmex/validation/)
- **Parent**: [Modules](../README.md)
