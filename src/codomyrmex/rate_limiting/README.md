# Rate Limiting Module

**Version**: v0.1.0 | **Status**: Active

API rate limiting with fixed window, sliding window, and token bucket algorithms.

## Quick Start

```python
from codomyrmex.rate_limiting import (
    SlidingWindowLimiter, TokenBucketLimiter, create_limiter, RateLimitExceeded
)

# Sliding window: 100 requests per minute
limiter = SlidingWindowLimiter(limit=100, window_seconds=60)

try:
    result = limiter.acquire("user-123")
    print(f"Allowed, {result.remaining} requests remaining")
except RateLimitExceeded as e:
    print(f"Rate limited, retry after {e.retry_after}s")

# Token bucket: burst + refill
bucket = TokenBucketLimiter(capacity=10, refill_rate=1.0)  # 10 tokens, 1/sec refill
bucket.acquire("api-key")  # Consumes 1 token

# Factory function
limiter = create_limiter("sliding_window", limit=1000, window_seconds=3600)
```

## Exports

| Class | Description |
|-------|-------------|
| `FixedWindowLimiter` | Fixed time window rate limiting |
| `SlidingWindowLimiter` | Rolling window rate limiting |
| `TokenBucketLimiter` | Token bucket with refill rate |
| `QuotaManager` | Combine multiple limiters per key |
| `RateLimitResult` | Result with remaining, limit, reset_at, headers |
| `RateLimitExceeded` | Exception with retry_after |
| `create_limiter(algorithm)` | Factory for creating limiters |

## HTTP Headers

```python
result = limiter.acquire("user-123")
headers = result.headers
# {'X-RateLimit-Limit': '100', 'X-RateLimit-Remaining': '99', 'X-RateLimit-Reset': '1700000000'}
```

## Navigation

- [SPEC](SPEC.md) | [AGENTS](AGENTS.md) | [PAI](PAI.md)
