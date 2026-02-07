# Networking — Functional Specification

**Module**: `codomyrmex.networking`  
**Version**: v0.1.0  
**Status**: Active

## 1. Overview

Networking module for Codomyrmex.

## 2. Architecture

### Components

| Component | Type | Description |
|-----------|------|-------------|
| `get_http_client()` | Function | Get an HTTP client instance. |

### Source Files

- `exceptions.py`
- `http_client.py`
- `raw_sockets.py`
- `ssh_sftp.py`
- `websocket_client.py`

## 3. Dependencies

See `src/codomyrmex/networking/__init__.py` for import dependencies.

## 4. Public API

```python
from codomyrmex.networking import get_http_client
```

## 5. Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k networking -v
```

## References

- [README.md](README.md) — Human-readable documentation
- [AGENTS.md](AGENTS.md) — Agent coordination guide
- [Source Code](../../../src/codomyrmex/networking/)
