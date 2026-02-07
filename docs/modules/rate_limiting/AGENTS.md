# Rate Limiting Module — Agent Coordination

## Purpose

API rate limiting, throttling, and quota management.

## Key Capabilities

- **RateLimitExceeded**: Raised when rate limit is exceeded.
- **RateLimitResult**: Result of a rate limit check.
- **RateLimiter**: Abstract base class for rate limiters.
- **FixedWindowLimiter**: Fixed window rate limiter.
- **SlidingWindowLimiter**: Sliding window rate limiter.
- `create_limiter()`: Create a rate limiter.
- `headers()`: Get rate limit headers for HTTP responses.
- `check()`: Check if request is allowed without consuming quota.

## Agent Usage Patterns

```python
from codomyrmex.rate_limiting import RateLimitExceeded

# Agent initializes rate limiting
instance = RateLimitExceeded()
```

## Integration Points

- **Source**: [src/codomyrmex/rate_limiting/](../../../src/codomyrmex/rate_limiting/)
- **Docs**: [Module Documentation](README.md)
- **Spec**: [Technical Specification](SPEC.md)

## Testing Guidelines

```bash
uv run python -m pytest src/codomyrmex/tests/ -k rate_limiting -v
```

- Run tests before and after making changes.
- Ensure all existing tests pass before submitting.
