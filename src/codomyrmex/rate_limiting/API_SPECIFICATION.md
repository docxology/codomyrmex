# Rate Limiting API Specification

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The `rate_limiting` module provides thread-safe rate limiting with multiple algorithms (fixed window, sliding window, token bucket) and a quota manager for composing multiple limits per key. All limiters implement a common `RateLimiter` ABC.

## Core API

### RateLimitResult (dataclass)

```python
from codomyrmex.rate_limiting import RateLimitResult

result = RateLimitResult(allowed=True, remaining=8, limit=10, reset_at=datetime(...), retry_after=None)
result.headers  # -> {"X-RateLimit-Limit": "10", "X-RateLimit-Remaining": "8", "X-RateLimit-Reset": "..."}
```

| Field | Type | Description |
|:------|:-----|:------------|
| `allowed` | `bool` | Whether the request is permitted |
| `remaining` | `int` | Remaining quota in the current window |
| `limit` | `int` | Total limit for the window |
| `reset_at` | `datetime \| None` | When the current window resets |
| `retry_after` | `float \| None` | Seconds to wait before retrying |

### RateLimiter (ABC)

All limiter classes implement this interface:

| Method | Signature | Description |
|:-------|:----------|:------------|
| `check` | `(key: str, cost: int = 1) -> RateLimitResult` | Check quota without consuming it |
| `acquire` | `(key: str, cost: int = 1) -> RateLimitResult` | Consume quota; raises `RateLimitExceeded` if over limit |
| `reset` | `(key: str) -> None` | Reset all quota for a given key |

### Limiter Implementations

```python
from codomyrmex.rate_limiting import FixedWindowLimiter, SlidingWindowLimiter, TokenBucketLimiter

# Fixed window: 100 requests per 60-second window
limiter = FixedWindowLimiter(limit=100, window_seconds=60)

# Sliding window: 100 requests in any rolling 60-second span
limiter = SlidingWindowLimiter(limit=100, window_seconds=60)

# Token bucket: capacity 100, refills 10 tokens/second
limiter = TokenBucketLimiter(capacity=100, refill_rate=10.0, refill_interval=1.0)

result = limiter.acquire("user-123", cost=1)
```

### QuotaManager

Composes multiple limiters and enforces all of them atomically.

```python
from codomyrmex.rate_limiting import QuotaManager, SlidingWindowLimiter, TokenBucketLimiter

manager = QuotaManager()
manager.add_limiter("per_minute", SlidingWindowLimiter(limit=60, window_seconds=60))
manager.add_limiter("burst", TokenBucketLimiter(capacity=10, refill_rate=2.0))

results = manager.acquire_all("user-123")     # dict[str, RateLimitResult]
checks  = manager.check_all("user-123")       # non-consuming check
```

### Factory Function

```python
from codomyrmex.rate_limiting import create_limiter

limiter = create_limiter(algorithm="sliding_window", limit=100, window_seconds=60)
limiter = create_limiter(algorithm="token_bucket", limit=50, window_seconds=30, refill_rate=5.0)
```

`algorithm` accepts: `"fixed_window"`, `"sliding_window"`, `"token_bucket"`.

## Error Handling

| Exception | Attributes | Raised When |
|:----------|:-----------|:------------|
| `RateLimitExceeded` | `retry_after: float \| None` | `acquire()` called when quota is exhausted |
| `ValueError` | -- | Unknown algorithm passed to `create_limiter()` |

## Thread Safety

All limiter implementations use `threading.Lock` internally. Safe for concurrent use across threads.

## Integration Points

- `logging_monitoring` -- All rate limit events can be logged for observability
- `api` -- `RateLimitResult.headers` provides standard HTTP rate-limit response headers
- `cache` -- Can pair with cache backends for distributed quota persistence

## Navigation

- **Human Documentation**: [README.md](README.md)
- **MCP Tools**: [MCP_TOOL_SPECIFICATION.md](MCP_TOOL_SPECIFICATION.md)
- **Parent Directory**: [codomyrmex](../README.md)
