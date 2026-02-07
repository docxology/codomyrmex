# Rate Limiting — Functional Specification

**Module**: `codomyrmex.rate_limiting`  
**Version**: v0.1.0  
**Status**: Active

## 1. Overview

API rate limiting, throttling, and quota management.

## 2. Architecture

### Components

| Component | Type | Description |
|-----------|------|-------------|
| `RateLimitExceeded` | Class | Raised when rate limit is exceeded. |
| `RateLimitResult` | Class | Result of a rate limit check. |
| `RateLimiter` | Class | Abstract base class for rate limiters. |
| `FixedWindowLimiter` | Class | Fixed window rate limiter. |
| `SlidingWindowLimiter` | Class | Sliding window rate limiter. |
| `TokenBucketLimiter` | Class | Token bucket rate limiter. |
| `QuotaManager` | Class | Manage multiple rate limits per key. |
| `create_limiter()` | Function | Create a rate limiter. |
| `headers()` | Function | Get rate limit headers for HTTP responses. |
| `check()` | Function | Check if request is allowed without consuming quota. |
| `acquire()` | Function | Acquire quota for a request. |
| `reset()` | Function | Reset quota for a key. |

### Source Files

- `distributed.py`

## 3. Dependencies

See `src/codomyrmex/rate_limiting/__init__.py` for import dependencies.

## 4. Public API

```python
from codomyrmex.rate_limiting import RateLimitExceeded, RateLimitResult, RateLimiter, FixedWindowLimiter, SlidingWindowLimiter
```

## 5. Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k rate_limiting -v
```

## References

- [README.md](README.md) — Human-readable documentation
- [AGENTS.md](AGENTS.md) — Agent coordination guide
- [Source Code](../../../src/codomyrmex/rate_limiting/)
