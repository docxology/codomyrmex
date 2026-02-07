# Utilities — Functional Specification

**Module**: `codomyrmex.utils`  
**Version**: v0.1.0  
**Status**: Active

## 1. Overview

Utilities Package.

## 2. Architecture

### Components

| Component | Type | Description |
|-----------|------|-------------|
| `ensure_directory()` | Function | Ensure a directory exists, creating it if necessary. |
| `safe_json_loads()` | Function | Safely parse JSON with a fallback default. |
| `safe_json_dumps()` | Function | Safely serialize to JSON with fallback. |
| `hash_content()` | Function | Generate hash of content. |
| `hash_file()` | Function | Generate hash of file contents. |

### Source Files

- `cli_helpers.py`
- `integration.py`
- `metrics.py`
- `refined.py`
- `script_base.py`
- `subprocess.py`

## 3. Dependencies

See `src/codomyrmex/utils/__init__.py` for import dependencies.

## 4. Public API

```python
from codomyrmex.utils import ensure_directory, safe_json_loads, safe_json_dumps, hash_content, hash_file
```

## 5. Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k utils -v
```
