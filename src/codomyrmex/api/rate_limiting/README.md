# rate_limiting

**Version**: v1.3.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Module implementation, resources, and local coordination for Rate Limiting.

## Quota and timing contracts

`FixedWindowLimiter`, `SlidingWindowLimiter`, and `TokenBucketLimiter` reject invalid configuration and negative/noninteger costs with `ValueError`. Zero cost is a quota no-op. A fresh key cannot exceed its configured capacity.

Sliding and token bucket limiters accept a keyword-only `clock` callable, defaulting to `time.monotonic`, for elapsed-time accounting. Public `reset_at` values remain wall-clock datetimes. Sliding weighted requests report the delay until enough entries expire; an oversized sliding/token request has no finite retry delay. See [SPEC.md](SPEC.md) for boundary and concurrency guarantees.

Deterministic real-instance regression checks:

```bash
uv run --locked pytest -q tests/unit/api/rate_limiting tests/unit/rate_limiting
```

## Directory Contents

- `PAI.md` – File
- `README.md` – File
- `SPEC.md` – File
- `__init__.py` – File
- `distributed.py` – File
- `limiters.py` – File
- `models.py` – File
- `py.typed` – File
- `strategies.py` – File

## Navigation

- **Parent Directory**: [api](../README.md)
- **Project Root**: ../../../../README.md

## Related Documents

- **Agents**: [AGENTS.md](AGENTS.md)
