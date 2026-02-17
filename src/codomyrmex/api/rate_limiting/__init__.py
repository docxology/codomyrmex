"""
Rate Limiting Module

Rate limiting with fixed window, sliding window, and token bucket algorithms.
"""

from .models import RateLimitExceeded, RateLimitResult
from .limiters import (
    FixedWindowLimiter,
    RateLimiter,
    SlidingWindowLimiter,
    TokenBucketLimiter,
)
from .strategies import QuotaManager, create_limiter

# Shared schemas for cross-module interop
try:
    from codomyrmex.validation.schemas import Result, ResultStatus
except ImportError:
    Result = None
    ResultStatus = None


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
    "RateLimitExceeded",
    "RateLimitResult",
    "RateLimiter",
    "FixedWindowLimiter",
    "SlidingWindowLimiter",
    "TokenBucketLimiter",
    "QuotaManager",
    "create_limiter",
    # CLI integration
    "cli_commands",
]
