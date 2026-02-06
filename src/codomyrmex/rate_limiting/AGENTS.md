# Agent Guidelines - Rate Limiting

## Module Overview

API rate limiting with fixed window, sliding window, and token bucket algorithms.

## Key Classes

- **FixedWindowLimiter** — Reset at fixed intervals
- **SlidingWindowLimiter** — Rolling window for accuracy
- **TokenBucketLimiter** — Burst-tolerant with refill
- **QuotaManager** — Combine multiple limiters
- **RateLimitResult** — Result with remaining count, reset time

## Agent Instructions

1. **Choose the right algorithm** — Use sliding window for accuracy, token bucket for bursts
2. **Handle RateLimitExceeded** — Always catch and implement retry with backoff
3. **Use HTTP headers** — Return `X-RateLimit-*` headers from `result.headers`
4. **Key by identifier** — Use user_id, API key, or IP for rate limit keys
5. **Monitor quotas** — Use `QuotaManager` for tiered rate limits

## Integration Points

- **api** — Protect endpoints from abuse
- **llm** — Limit API calls to providers
- **cloud** — Respect provider rate limits

## Testing Patterns

```python
# Test rate limiting works
limiter = SlidingWindowLimiter(limit=2, window_seconds=60)
limiter.acquire("key")
limiter.acquire("key")

with pytest.raises(RateLimitExceeded) as exc:
    limiter.acquire("key")
assert exc.value.retry_after > 0

# Verify headers
result = limiter.acquire("other-key")
assert "X-RateLimit-Remaining" in result.headers
```

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)
