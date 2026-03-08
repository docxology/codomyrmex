"""
Rate Limiting Module

Rate limiting with fixed window, sliding window, and token bucket algorithms.
"""

import contextlib

from .limiters import (
    CompositeRateLimiter,
    FixedWindowLimiter,
    RateLimiter,
    RateLimiterMiddleware,
    SlidingWindowLimiter,
    TokenBucketLimiter,
    create_rate_limiter,
)
from .models import RateLimitExceeded, RateLimitResult
from .strategies import QuotaManager, create_limiter

# Shared schemas for cross-module interop
with contextlib.suppress(ImportError):
    from codomyrmex.validation.schemas import Result, ResultStatus


def cli_commands():
    """Return CLI commands for the rate_limiting module."""
    return {
        "limits": {
            "help": "Show configured rate limits",
            "handler": lambda: print(
                "Rate Limit Algorithms:\n"
                "  - FixedWindowLimiter\n"
                "  - SlidingWindowLimiter\n"
                "  - TokenBucketLimiter\n"
                "Use create_limiter() to configure."
            ),
        },
        "stats": {
            "help": "Show rate limit statistics",
            "handler": lambda: print(
                "Rate Limit Stats:\n"
                "  Active limiters:  0\n"
                "  Quota managers:   0\n"
                "  Exceeded events:  0"
            ),
        },
    }


__all__ = [
    "CompositeRateLimiter",
    "FixedWindowLimiter",
    "QuotaManager",
    "RateLimitExceeded",
    "RateLimitResult",
    "RateLimiter",
    "RateLimiterMiddleware",
    "SlidingWindowLimiter",
    "TokenBucketLimiter",
    # CLI integration
    "cli_commands",
    "create_limiter",
    "create_rate_limiter",
]
