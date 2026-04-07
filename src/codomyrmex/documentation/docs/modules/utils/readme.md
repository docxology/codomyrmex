# utils

**Version**: v1.2.8 | **Status**: Active | **Last Updated**: April 2026

## Overview

Cross-cutting helpers: JSON safety, hashing, paths, subprocess execution (`process/`), script base classes, metrics hooks, and **two retry surfaces** (see below). Depends on `codomyrmex.logging_monitoring` for structured logging.

## Retry: package vs `retry_sync`

| Surface | Import | Use when |
|--------|--------|----------|
| **Package `retry`** | `from codomyrmex.utils import retry` | Simple sync retries: `max_attempts`, `delay`, `backoff`, `exceptions`. |
| **`retry_sync` module** | `from codomyrmex.utils.retry_sync import retry, async_retry` | Jitter, capped delay, `RetryConfig`, and **async** retries via `async_retry`. Also re-exported on the package: `RetryConfig`, `async_retry` (see `__all__`). |

The implementation file is named `retry_sync.py` so a `retry` **submodule** cannot shadow the package-level `retry` decorator.

## Key references

- [API_SPECIFICATION.md](API_SPECIFICATION.md) — function-level API
- [SPEC.md](SPEC.md) — design contracts
- [PAI.md](PAI.md) — PAI integration notes
- Tests: `uv run pytest src/codomyrmex/tests/unit/utils/ -q`

## Directory contents

- `__init__.py` — public exports (`__all__`)
- `retry_sync.py` — configurable sync/async retry
- `process/` — subprocess, script base, advanced streaming
- `mcp_tools.py`, `metrics.py`, `integration.py`, `refined.py`, `graph.py`, `hashing.py`, `cli_helpers.py`
- `i18n/` — localized strings

## Navigation

- **Parent**: [codomyrmex](../README.md)
- **Project root**: [../../../README.md](../../../README.md)
