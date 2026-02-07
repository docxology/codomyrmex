# Authentication — Functional Specification

**Module**: `codomyrmex.auth`  
**Version**: v0.1.0  
**Status**: Active

## 1. Overview

Authentication module for Codomyrmex.

## 2. Architecture

### Components

| Component | Type | Description |
|-----------|------|-------------|
| `authenticate()` | Function | Authenticate with credentials. |
| `authorize()` | Function | Check if token has permission. |
| `get_authenticator()` | Function | Get an authenticator instance. |

### Source Files

- `api_key_manager.py`
- `authenticator.py`
- `permissions.py`
- `token.py`
- `validator.py`

## 3. Dependencies

See `src/codomyrmex/auth/__init__.py` for import dependencies.

## 4. Public API

```python
from codomyrmex.auth import authenticate, authorize, get_authenticator
```

## 5. Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k auth -v
```
