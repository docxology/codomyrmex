# Rate Limiting Module

API rate limiting, throttling, and quota management.

## Algorithms

| Algorithm | Best For |
|-----------|----------|
| `FixedWindowLimiter` | Simple, low-memory limits |
| `SlidingWindowLimiter` | Accurate, smooth limiting |
| `TokenBucketLimiter` | Burst-tolerant quotas |

## Quick Start

```python
from codomyrmex.rate_limiting import (
    SlidingWindowLimiter,
    RateLimitExceeded,
    create_limiter,
)

# 100 requests per minute
limiter = create_limiter(limit=100, window_seconds=60)

try:
    result = limiter.acquire(user_id)
    print(f"Remaining: {result.remaining}")
except RateLimitExceeded as e:
    print(f"Retry after: {e.retry_after}s")
```

## Navigation

- [Technical Spec](SPEC.md) | [Agent Guidelines](AGENTS.md) | [PAI Context](PAI.md)
