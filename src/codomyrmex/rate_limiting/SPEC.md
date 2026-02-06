# Technical Specification - Rate Limiting

**Module**: `codomyrmex.rate_limiting` | **Version**: v0.1.0 | **Updated**: February 2026

## Public API

```python
from codomyrmex.rate_limiting import (
    RateLimiter, FixedWindowLimiter, SlidingWindowLimiter,
    TokenBucketLimiter, QuotaManager, RateLimitResult,
    RateLimitExceeded, create_limiter,
)
```

## Testing

```bash
pytest tests/unit/test_rate_limiting.py -v
```
