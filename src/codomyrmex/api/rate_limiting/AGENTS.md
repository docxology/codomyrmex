# AI Agent Guidelines — api/rate_limiting

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Provides rate limiting for API endpoints with multiple algorithms (fixed window, sliding window, token bucket), composite limiting, distributed Redis-backed limiting, and middleware wrappers.

## Key Components

| Component | File | Role |
|-----------|------|------|
| `RateLimiter` | `limiters.py` | ABC defining `check`, `acquire`, `reset`, and `consume` methods |
| `FixedWindowLimiter` | `limiters.py` | Time-windowed counter with thread-safe locking |
| `SlidingWindowLimiter` | `limiters.py` | Deque-based sliding window tracking individual request timestamps |
| `TokenBucketLimiter` | `limiters.py` | Token bucket with configurable capacity, refill rate, and initial tokens |
| `CompositeRateLimiter` | `limiters.py` | Enforces multiple limiters simultaneously; request allowed only if all pass |
| `RateLimiterMiddleware` | `limiters.py` | Wrapper providing `check` (acquire-or-deny) and `would_allow` (peek) methods |
| `RateLimitResult` | `models.py` | Dataclass with `allowed`, `remaining`, `limit`, `reset_at`, `retry_after`; generates HTTP headers |
| `RateLimitExceeded` | `models.py` | Exception with `retry_after` field |
| `QuotaManager` | `strategies.py` | Manages multiple named limiters per key; atomic `acquire_all` |
| `RedisRateLimiter` | `distributed.py` | Redis-backed limiter with local fallback |
| `LeakyBucketLimiter` | `distributed.py` | Leaky bucket algorithm variant |
| `AdaptiveRateLimiter` | `distributed.py` | Adjusts limits based on system load metrics |
| `create_limiter` | `strategies.py` | Factory function selecting algorithm by name string |
| `create_rate_limiter` | `limiters.py` | Factory function selecting algorithm by strategy name |

## Operating Contracts

- `check(key, cost)` inspects quota without consuming; `acquire(key, cost)` consumes and raises `RateLimitExceeded` on failure.
- `consume(key, cost)` is a convenience wrapper that catches `RateLimitExceeded` and returns a denied `RateLimitResult` instead.
- `RateLimitResult.headers` / `to_headers()` produces standard `X-RateLimit-*` and `Retry-After` HTTP headers.
- All in-memory limiters are thread-safe via `threading.Lock`.
- `CompositeRateLimiter` returns the most restrictive result across all constituent limiters.

## Integration Points

- **Parent**: `api` module applies rate limiters as middleware in request pipelines.
- **Consumers**: REST API endpoints, MCP bridge, webhook dispatchers.
- **Distributed**: `RedisRateLimiter` requires a Redis connection; falls back to local limiting if unavailable.

## Navigation

- **Parent**: [api/README.md](../README.md)
- **Sibling**: [SPEC.md](SPEC.md) | [README.md](README.md)
- **Root**: [../../../../README.md](../../../../README.md)
