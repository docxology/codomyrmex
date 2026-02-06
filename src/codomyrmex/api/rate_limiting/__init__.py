"""
API Rate Limiting utilities.

Provides rate limiters and quota management for API endpoints.
"""

import hashlib
import threading
import time
from abc import ABC, abstractmethod
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, Optional, Tuple


@dataclass
class RateLimitResult:
    """Result of a rate limit check."""
    allowed: bool
    limit: int
    remaining: int
    reset_at: datetime
    retry_after: float | None = None

    def to_headers(self) -> dict[str, str]:
        """Convert to HTTP headers."""
        headers = {
            "X-RateLimit-Limit": str(self.limit),
            "X-RateLimit-Remaining": str(self.remaining),
            "X-RateLimit-Reset": str(int(self.reset_at.timestamp())),
        }
        if self.retry_after is not None:
            headers["Retry-After"] = str(int(self.retry_after))
        return headers


class RateLimiter(ABC):
    """Abstract base class for rate limiters."""

    @abstractmethod
    def check(self, key: str) -> RateLimitResult:
        """Check if a request is allowed."""
        pass

    @abstractmethod
    def consume(self, key: str, tokens: int = 1) -> RateLimitResult:
        """Consume tokens and check if allowed."""
        pass

    @abstractmethod
    def reset(self, key: str) -> None:
        """Reset the rate limit for a key."""
        pass


class FixedWindowLimiter(RateLimiter):
    """Fixed window rate limiter."""

    def __init__(self, limit: int, window_seconds: int = 60):
        self.limit = limit
        self.window_seconds = window_seconds
        self._windows: dict[str, tuple[datetime, int]] = {}
        self._lock = threading.RLock()

    def _get_window_start(self) -> datetime:
        now = datetime.now()
        seconds_since_epoch = int(now.timestamp())
        window_start_epoch = (seconds_since_epoch // self.window_seconds) * self.window_seconds
        return datetime.fromtimestamp(window_start_epoch)

    def check(self, key: str) -> RateLimitResult:
        with self._lock:
            window_start = self._get_window_start()
            reset_at = window_start + timedelta(seconds=self.window_seconds)

            if key in self._windows:
                cached_start, count = self._windows[key]
                if cached_start == window_start:
                    remaining = max(0, self.limit - count)
                    if count >= self.limit:
                        return RateLimitResult(
                            allowed=False,
                            limit=self.limit,
                            remaining=0,
                            reset_at=reset_at,
                            retry_after=(reset_at - datetime.now()).total_seconds()
                        )
                    return RateLimitResult(
                        allowed=True,
                        limit=self.limit,
                        remaining=remaining,
                        reset_at=reset_at
                    )

            return RateLimitResult(
                allowed=True,
                limit=self.limit,
                remaining=self.limit,
                reset_at=reset_at
            )

    def consume(self, key: str, tokens: int = 1) -> RateLimitResult:
        with self._lock:
            window_start = self._get_window_start()
            reset_at = window_start + timedelta(seconds=self.window_seconds)

            if key in self._windows:
                cached_start, count = self._windows[key]
                if cached_start != window_start:
                    count = 0
            else:
                count = 0

            if count + tokens > self.limit:
                return RateLimitResult(
                    allowed=False,
                    limit=self.limit,
                    remaining=max(0, self.limit - count),
                    reset_at=reset_at,
                    retry_after=(reset_at - datetime.now()).total_seconds()
                )

            self._windows[key] = (window_start, count + tokens)

            return RateLimitResult(
                allowed=True,
                limit=self.limit,
                remaining=max(0, self.limit - count - tokens),
                reset_at=reset_at
            )

    def reset(self, key: str) -> None:
        with self._lock:
            if key in self._windows:
                del self._windows[key]


class SlidingWindowLimiter(RateLimiter):
    """Sliding window rate limiter for smoother rate limiting."""

    def __init__(self, limit: int, window_seconds: int = 60):
        self.limit = limit
        self.window_seconds = window_seconds
        self._requests: dict[str, list] = defaultdict(list)
        self._lock = threading.RLock()

    def _clean_old_requests(self, key: str) -> None:
        """Remove requests outside the window."""
        cutoff = time.time() - self.window_seconds
        self._requests[key] = [t for t in self._requests[key] if t > cutoff]

    def check(self, key: str) -> RateLimitResult:
        with self._lock:
            self._clean_old_requests(key)
            count = len(self._requests[key])
            remaining = max(0, self.limit - count)
            reset_at = datetime.now() + timedelta(seconds=self.window_seconds)

            if count >= self.limit:
                oldest = min(self._requests[key]) if self._requests[key] else time.time()
                retry_after = oldest + self.window_seconds - time.time()
                return RateLimitResult(
                    allowed=False,
                    limit=self.limit,
                    remaining=0,
                    reset_at=reset_at,
                    retry_after=max(0, retry_after)
                )

            return RateLimitResult(
                allowed=True,
                limit=self.limit,
                remaining=remaining,
                reset_at=reset_at
            )

    def consume(self, key: str, tokens: int = 1) -> RateLimitResult:
        with self._lock:
            self._clean_old_requests(key)
            count = len(self._requests[key])
            reset_at = datetime.now() + timedelta(seconds=self.window_seconds)

            if count + tokens > self.limit:
                oldest = min(self._requests[key]) if self._requests[key] else time.time()
                retry_after = oldest + self.window_seconds - time.time()
                return RateLimitResult(
                    allowed=False,
                    limit=self.limit,
                    remaining=max(0, self.limit - count),
                    reset_at=reset_at,
                    retry_after=max(0, retry_after)
                )

            current_time = time.time()
            for _ in range(tokens):
                self._requests[key].append(current_time)

            return RateLimitResult(
                allowed=True,
                limit=self.limit,
                remaining=max(0, self.limit - count - tokens),
                reset_at=reset_at
            )

    def reset(self, key: str) -> None:
        with self._lock:
            self._requests[key] = []


class TokenBucketLimiter(RateLimiter):
    """Token bucket rate limiter for burst handling."""

    def __init__(
        self,
        capacity: int,
        refill_rate: float,  # tokens per second
        initial_tokens: int | None = None
    ):
        self.capacity = capacity
        self.refill_rate = refill_rate
        self._buckets: dict[str, tuple[float, float]] = {}  # key -> (tokens, last_update)
        self._lock = threading.RLock()
        self._initial_tokens = initial_tokens if initial_tokens is not None else capacity

    def _refill(self, key: str) -> float:
        """Refill tokens based on elapsed time."""
        now = time.time()

        if key not in self._buckets:
            self._buckets[key] = (float(self._initial_tokens), now)
            return float(self._initial_tokens)

        tokens, last_update = self._buckets[key]
        elapsed = now - last_update
        new_tokens = min(self.capacity, tokens + elapsed * self.refill_rate)
        self._buckets[key] = (new_tokens, now)

        return new_tokens

    def check(self, key: str) -> RateLimitResult:
        with self._lock:
            tokens = self._refill(key)
            remaining = int(tokens)
            reset_at = datetime.now() + timedelta(seconds=self.capacity / self.refill_rate)

            return RateLimitResult(
                allowed=tokens >= 1,
                limit=self.capacity,
                remaining=remaining,
                reset_at=reset_at,
                retry_after=(1 - tokens) / self.refill_rate if tokens < 1 else None
            )

    def consume(self, key: str, tokens: int = 1) -> RateLimitResult:
        with self._lock:
            available = self._refill(key)
            reset_at = datetime.now() + timedelta(seconds=self.capacity / self.refill_rate)

            if available < tokens:
                wait_time = (tokens - available) / self.refill_rate
                return RateLimitResult(
                    allowed=False,
                    limit=self.capacity,
                    remaining=int(available),
                    reset_at=reset_at,
                    retry_after=wait_time
                )

            current_tokens, last_update = self._buckets[key]
            self._buckets[key] = (current_tokens - tokens, last_update)

            return RateLimitResult(
                allowed=True,
                limit=self.capacity,
                remaining=int(available - tokens),
                reset_at=reset_at
            )

    def reset(self, key: str) -> None:
        with self._lock:
            if key in self._buckets:
                del self._buckets[key]


class CompositeRateLimiter(RateLimiter):
    """Combines multiple rate limiters."""

    def __init__(self, limiters: dict[str, RateLimiter]):
        self.limiters = limiters

    def check(self, key: str) -> RateLimitResult:
        results = [(name, limiter.check(key)) for name, limiter in self.limiters.items()]

        # Return the most restrictive result
        for name, result in results:
            if not result.allowed:
                return result

        # All allowed, return the one with least remaining
        return min(results, key=lambda x: x[1].remaining)[1]

    def consume(self, key: str, tokens: int = 1) -> RateLimitResult:
        # First check all limiters
        for limiter in self.limiters.values():
            result = limiter.check(key)
            if not result.allowed:
                return result

        # All allowed, consume from all
        results = []
        for limiter in self.limiters.values():
            results.append(limiter.consume(key, tokens))

        # Return most restrictive
        return min(results, key=lambda x: x.remaining)

    def reset(self, key: str) -> None:
        for limiter in self.limiters.values():
            limiter.reset(key)


def create_rate_limiter(
    limiter_type: str,
    **kwargs
) -> RateLimiter:
    """Factory function to create rate limiters."""
    limiters = {
        "fixed_window": FixedWindowLimiter,
        "sliding_window": SlidingWindowLimiter,
        "token_bucket": TokenBucketLimiter,
    }

    limiter_class = limiters.get(limiter_type)
    if not limiter_class:
        raise ValueError(f"Unknown limiter type: {limiter_type}")

    return limiter_class(**kwargs)


class RateLimitStrategy(Enum):
    """Rate limiting strategies."""
    FIXED_WINDOW = "fixed_window"
    SLIDING_WINDOW = "sliding_window"
    TOKEN_BUCKET = "token_bucket"


class RateLimiterMiddleware:
    """
    Middleware for applying rate limits.

    Usage:
        limiter = RateLimiterMiddleware(
            FixedWindowLimiter(limit=100, window_seconds=60)
        )

        def get_key(request):
            return request.client_ip

        def handle_request(request):
            result = limiter.check(get_key(request))
            if not result.allowed:
                return {"error": "Rate limited"}, 429, result.to_headers()
            return process(request)
    """

    def __init__(self, limiter: RateLimiter):
        self.limiter = limiter

    def check(self, key: str) -> RateLimitResult:
        """Check and acquire rate limit."""
        return self.limiter.consume(key)

    def would_allow(self, key: str) -> bool:
        """Check if request would be allowed without consuming."""
        return self.limiter.check(key).allowed


__all__ = [
    # Enums
    "RateLimitStrategy",
    # Data classes
    "RateLimitResult",
    # Abstract base
    "RateLimiter",
    # Limiters
    "FixedWindowLimiter",
    "SlidingWindowLimiter",
    "TokenBucketLimiter",
    "CompositeRateLimiter",
    # Middleware
    "RateLimiterMiddleware",
    # Factory
    "create_rate_limiter",
]
