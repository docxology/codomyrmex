# Cloud — Functional Specification

**Module**: `codomyrmex.cloud`  
**Version**: v0.1.7  
**Status**: Active

## 1. Overview

Cloud Services Module for Codomyrmex.

## 2. Architecture

### Components

| Component | Type | Description |
|-----------|------|-------------|

### Submodule Structure

- `aws/` — AWS integration submodule.
- `azure/` — Azure integration submodule.
- `coda_io/` — Coda.io API Client Submodule.
- `common/` — Cloud common utilities.
- `gcp/` — GCP integration submodule.
- `infomaniak/` — Infomaniak Public Cloud Integration.

### Source Files

- `edge.py`

## 3. Dependencies

See `src/codomyrmex/cloud/__init__.py` for import dependencies.

## 4. Public API

See source module for available exports.

## 5. Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k cloud -v
```

## References

- [README.md](README.md) — Human-readable documentation
- [AGENTS.md](AGENTS.md) — Agent coordination guide
- [Source Code](../../../src/codomyrmex/cloud/)
