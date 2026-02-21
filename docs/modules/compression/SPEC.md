# Compression — Functional Specification

**Module**: `codomyrmex.compression`  
**Version**: v1.0.0  
**Status**: Active

## 1. Overview

Compression module for Codomyrmex.

## 2. Architecture

### Components

| Component | Type | Description |
|-----------|------|-------------|
| `compress()` | Function | Compress data. |
| `decompress()` | Function | Decompress data. |
| `get_compressor()` | Function | Get a compressor instance. |
| `compress_file()` | Function | Compress a file. |
| `decompress_file()` | Function | Decompress a file. |

### Source Files

- `archive_manager.py`
- `compressor.py`
- `parallel.py`
- `zstd_compressor.py`

## 3. Dependencies

See `src/codomyrmex/compression/__init__.py` for import dependencies.

## 4. Public API

```python
from codomyrmex.compression import compress, decompress, get_compressor, compress_file, decompress_file
```

## 5. Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k compression -v
```

## References

- [README.md](README.md) — Human-readable documentation
- [AGENTS.md](AGENTS.md) — Agent coordination guide
- [Source Code](../../../src/codomyrmex/compression/)
