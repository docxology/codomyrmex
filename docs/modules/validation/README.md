# Validation Module Documentation

**Version**: v0.1.7 | **Status**: Active | **Last Updated**: February 2026

## Overview

Validation module for Codomyrmex.

## Key Features

- `validate()` — Validate data against a schema.
- `is_valid()` — Check if data is valid against a schema.
- `get_errors()` — Get validation errors for data.

## Submodules

| Submodule | Description |
|-----------|-------------|
| `rules` | Rules Submodule |
| `sanitizers` | Sanitizers Submodule |
| `schemas` | Validation Schemas Module |

## Quick Start

```python
from codomyrmex.validation import validate, is_valid, get_errors

# Use the module
result = validate()
```


## Installation

```bash
uv pip install codomyrmex
```

## API Reference

### Functions

| Function | Description |
|----------|-------------|
| `validate()` | Validate data against a schema. |
| `is_valid()` | Check if data is valid against a schema. |
| `get_errors()` | Get validation errors for data. |

## Directory Contents

| File | Description |
|------|-------------|
| `README.md` | This documentation |
| `AGENTS.md` | Agent coordination guide |
| `SPEC.md` | Technical specification |


## Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k validation -v
```

## Navigation

- **Source**: [src/codomyrmex/validation/](../../../src/codomyrmex/validation/)
- **Parent**: [Modules](../README.md)
