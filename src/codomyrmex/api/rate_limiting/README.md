# api/rate_limiting

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

API rate limiting utilities. Provides thread-safe rate limiters and quota management for API endpoints. Includes three limiter algorithms (fixed window, sliding window, token bucket), a composite limiter for layered policies, and a middleware wrapper for easy integration. All limiters implement a common `RateLimiter` ABC and return `RateLimitResult` objects with HTTP header generation.

## Key Exports

### Enums

- **`RateLimitStrategy`** -- Rate limiting strategy enumeration (FIXED_WINDOW, SLIDING_WINDOW, TOKEN_BUCKET)

### Data Classes

- **`RateLimitResult`** -- Rate limit check result with allowed flag, limit, remaining count, reset time, and retry_after; includes `to_headers()` for generating X-RateLimit HTTP headers

### Abstract Base

- **`RateLimiter`** -- ABC defining `check(key)`, `consume(key, tokens)`, and `reset(key)` interface

### Limiter Implementations

- **`FixedWindowLimiter`** -- Fixed time-window rate limiter; resets counters at window boundaries
- **`SlidingWindowLimiter`** -- Sliding window rate limiter for smoother rate limiting; tracks individual request timestamps
- **`TokenBucketLimiter`** -- Token bucket rate limiter for burst handling; configurable capacity and refill rate
- **`CompositeRateLimiter`** -- Combines multiple rate limiters; enforces the most restrictive result across all child limiters

### Middleware

- **`RateLimiterMiddleware`** -- Middleware wrapper providing `check(key)` and `would_allow(key)` for easy integration into request pipelines

### Factory

- **`create_rate_limiter()`** -- Factory function to instantiate rate limiters by type string ("fixed_window", "sliding_window", "token_bucket")

## Directory Contents

- `__init__.py` - Package init; contains all rate limiting classes inline (single-file module)
- `py.typed` - PEP 561 type-checking marker

## Navigation

- **Parent Module**: [api](../README.md)
- **Project Root**: [../../../../README.md](../../../../README.md)
