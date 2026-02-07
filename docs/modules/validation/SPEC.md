# Validation — Functional Specification

**Module**: `codomyrmex.validation`  
**Version**: v0.1.0  
**Status**: Active

## 1. Overview

Validation module for Codomyrmex.

## 2. Architecture

### Components

| Component | Type | Description |
|-----------|------|-------------|
| `validate()` | Function | Validate data against a schema. |
| `is_valid()` | Function | Check if data is valid against a schema. |
| `get_errors()` | Function | Get validation errors for data. |

### Submodule Structure

- `rules/` — Rules Submodule
- `sanitizers/` — Sanitizers Submodule
- `schemas/` — Validation Schemas Module

### Source Files

- `contextual.py`
- `examples_validator.py`
- `exceptions.py`
- `parser.py`
- `summary.py`
- `validation_manager.py`
- `validator.py`

## 3. Dependencies

See `src/codomyrmex/validation/__init__.py` for import dependencies.

## 4. Public API

```python
from codomyrmex.validation import validate, is_valid, get_errors
```

## 5. Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k validation -v
```
