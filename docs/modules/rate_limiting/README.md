# Rate Limiting Module Documentation

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

API rate limiting, throttling, and quota management.

## Key Features

- **RateLimitExceeded** — Raised when rate limit is exceeded.
- **RateLimitResult** — Result of a rate limit check.
- **RateLimiter** — Abstract base class for rate limiters.
- **FixedWindowLimiter** — Fixed window rate limiter.
- **SlidingWindowLimiter** — Sliding window rate limiter.
- **TokenBucketLimiter** — Token bucket rate limiter.
- `create_limiter()` — Create a rate limiter.
- `headers()` — Get rate limit headers for HTTP responses.
- `check()` — Check if request is allowed without consuming quota.
- `acquire()` — Acquire quota for a request.

## Quick Start

```python
from codomyrmex.rate_limiting import RateLimitExceeded, RateLimitResult, RateLimiter

# Initialize
instance = RateLimitExceeded()
```


## Installation

```bash
pip install codomyrmex
```

## API Reference

### Classes

| Class | Description |
|-------|-------------|
| `RateLimitExceeded` | Raised when rate limit is exceeded. |
| `RateLimitResult` | Result of a rate limit check. |
| `RateLimiter` | Abstract base class for rate limiters. |
| `FixedWindowLimiter` | Fixed window rate limiter. |
| `SlidingWindowLimiter` | Sliding window rate limiter. |
| `TokenBucketLimiter` | Token bucket rate limiter. |
| `QuotaManager` | Manage multiple rate limits per key. |

### Functions

| Function | Description |
|----------|-------------|
| `create_limiter()` | Create a rate limiter. |
| `headers()` | Get rate limit headers for HTTP responses. |
| `check()` | Check if request is allowed without consuming quota. |
| `acquire()` | Acquire quota for a request. |
| `reset()` | Reset quota for a key. |
| `add_limiter()` | Add a named limiter. |
| `check_all()` | Check all limiters. |
| `acquire_all()` | Acquire from all limiters (atomic). |

## Directory Contents

| File | Description |
|------|-------------|
| `README.md` | This documentation |
| `AGENTS.md` | Agent coordination guide |
| `SPEC.md` | Technical specification |


## Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k rate_limiting -v
```

## Navigation

- **Source**: [src/codomyrmex/rate_limiting/](../../../src/codomyrmex/rate_limiting/)
- **Parent**: [Modules](../README.md)
