# api/rate_limiting — Functional Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

The rate limiting submodule provides multiple rate limiting algorithms, composite and distributed limiting, and HTTP middleware integration. All limiters share a common `RateLimiter` ABC.

## Architecture

```
rate_limiting/
├── __init__.py      # Re-exports from submodules
├── models.py        # RateLimitResult, RateLimitExceeded
├── limiters.py      # RateLimiter ABC, FixedWindow, SlidingWindow, TokenBucket, Composite, Middleware, factory
├── strategies.py    # QuotaManager, create_limiter convenience factory
├── distributed.py   # RedisRateLimiter, LeakyBucketLimiter, AdaptiveRateLimiter
```

## Key Classes

### RateLimiter (ABC) — `limiters.py`

| Method | Signature | Description |
|--------|-----------|-------------|
| `check` | `(key: str, cost: int = 1) -> RateLimitResult` | Inspect quota without consuming |
| `acquire` | `(key: str, cost: int = 1) -> RateLimitResult` | Consume quota; raises `RateLimitExceeded` on failure |
| `reset` | `(key: str) -> None` | Clear quota state for key |
| `consume` | `(key: str, cost: int = 1, *, tokens: int \| None = None) -> RateLimitResult` | Acquire-or-deny wrapper (never raises) |

### FixedWindowLimiter — `limiters.py`

| Constructor | `(limit: int, window_seconds: int)` |
|-------------|--------------------------------------|
| Behaviour | Counts requests per discrete time window; resets at window boundary |

### SlidingWindowLimiter — `limiters.py`

| Constructor | `(limit: int, window_seconds: int)` |
|-------------|--------------------------------------|
| Behaviour | Tracks individual request timestamps in a deque; evicts entries older than window |

### TokenBucketLimiter — `limiters.py`

| Constructor | `(capacity: int, refill_rate: float, refill_interval: float = 1.0, initial_tokens: int \| None = None)` |
|-------------|----------------------------------------------------------------------------------------------------------|
| Behaviour | Refills tokens at `refill_rate` per `refill_interval` seconds up to `capacity` |

### CompositeRateLimiter — `limiters.py`

| Constructor | `(limiters: dict[str, RateLimiter])` |
|-------------|---------------------------------------|
| Behaviour | All constituent limiters must allow; returns most restrictive result |

### RateLimiterMiddleware — `limiters.py`

| Method | Signature | Description |
|--------|-----------|-------------|
| `check` | `(key: str, cost: int = 1) -> RateLimitResult` | Acquire-or-deny (returns result, never raises) |
| `would_allow` | `(key: str, cost: int = 1) -> bool` | Peek without consuming |
| `reset` | `(key: str) -> None` | Reset underlying limiter |

### QuotaManager — `strategies.py`

| Method | Signature | Description |
|--------|-----------|-------------|
| `add_limiter` | `(name: str, limiter: RateLimiter) -> None` | Register a named limiter |
| `check_all` | `(key: str, cost: int = 1) -> dict[str, RateLimitResult]` | Check all limiters |
| `acquire_all` | `(key: str, cost: int = 1) -> dict[str, RateLimitResult]` | Atomic acquire from all; raises on first failure |

### RateLimitResult — `models.py`

| Field | Type | Description |
|-------|------|-------------|
| `allowed` | `bool` | Whether the request is permitted |
| `remaining` | `int` | Remaining quota in current window |
| `limit` | `int` | Total quota limit |
| `reset_at` | `datetime \| None` | When the window resets |
| `retry_after` | `float \| None` | Seconds until retry is possible |
| `headers` / `to_headers()` | `dict[str, str]` | `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`, `Retry-After` |

## Error Handling

- `RateLimitExceeded(message, retry_after)` raised by `acquire` when quota is exhausted.
- `consume` catches `RateLimitExceeded` and returns `RateLimitResult(allowed=False, ...)` instead.
- Thread safety guaranteed by `threading.Lock` in all in-memory limiter implementations.

## Dependencies

- `threading`, `time`, `collections.deque`, `datetime` (stdlib)
- `distributed.py`: optional Redis dependency for `RedisRateLimiter`

## Navigation

- **Parent**: [api/SPEC.md](../SPEC.md)
- **Sibling**: [AGENTS.md](AGENTS.md) | [README.md](README.md)
