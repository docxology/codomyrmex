"""
Rate Limiting Strategies

Quota management and convenience functions.
"""

from .models import RateLimitExceeded, RateLimitResult
from .limiters import (
    FixedWindowLimiter,
    RateLimiter,
    SlidingWindowLimiter,
    TokenBucketLimiter,
)


class QuotaManager:
    """Manage multiple rate limits per key."""

    def __init__(self):
        self._limiters: dict[str, RateLimiter] = {}

    def add_limiter(self, name: str, limiter: RateLimiter) -> None:
        """Add a named limiter."""
        self._limiters[name] = limiter

    def check_all(self, key: str, cost: int = 1) -> dict[str, RateLimitResult]:
        """Check all limiters."""
        return {
            name: limiter.check(key, cost)
            for name, limiter in self._limiters.items()
        }

    def acquire_all(self, key: str, cost: int = 1) -> dict[str, RateLimitResult]:
        """Acquire from all limiters (atomic)."""
        # First check all
        for name, limiter in self._limiters.items():
            result = limiter.check(key, cost)
            if not result.allowed:
                raise RateLimitExceeded(
                    f"Rate limit '{name}' exceeded for {key}",
                    retry_after=result.retry_after,
                )

        # Then acquire from all
        return {
            name: limiter.acquire(key, cost)
            for name, limiter in self._limiters.items()
        }


def create_limiter(
    algorithm: str = "sliding_window",
    limit: int = 100,
    window_seconds: int = 60,
    **kwargs,
) -> RateLimiter:
    """Create a rate limiter."""
    if algorithm == "fixed_window":
        return FixedWindowLimiter(limit, window_seconds)
    elif algorithm == "sliding_window":
        return SlidingWindowLimiter(limit, window_seconds)
    elif algorithm == "token_bucket":
        return TokenBucketLimiter(
            capacity=limit,
            refill_rate=kwargs.get("refill_rate", limit / window_seconds),
            refill_interval=kwargs.get("refill_interval", 1.0),
        )
    else:
        raise ValueError(f"Unknown algorithm: {algorithm}")
