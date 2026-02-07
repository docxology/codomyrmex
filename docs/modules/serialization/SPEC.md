# Serialization — Functional Specification

**Module**: `codomyrmex.serialization`  
**Version**: v0.1.0  
**Status**: Active

## 1. Overview

Serialization module for Codomyrmex.

## 2. Architecture

### Components

| Component | Type | Description |
|-----------|------|-------------|
| `serialize()` | Function | Serialize an object to bytes. |
| `deserialize()` | Function | Deserialize data to an object. |

### Source Files

- `binary_formats.py`
- `exceptions.py`
- `serialization_manager.py`
- `serializer.py`

## 3. Dependencies

See `src/codomyrmex/serialization/__init__.py` for import dependencies.

## 4. Public API

```python
from codomyrmex.serialization import serialize, deserialize
```

## 5. Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k serialization -v
```
