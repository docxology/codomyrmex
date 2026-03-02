"""
Rate Limiters

Rate limiter implementations: fixed window, sliding window, token bucket.
"""

import threading
import time
from abc import ABC, abstractmethod
from collections import deque
from datetime import datetime, timedelta

from .models import RateLimitExceeded, RateLimitResult


class RateLimiter(ABC):
    """Abstract base class for rate limiters."""

    @abstractmethod
    def check(self, key: str, cost: int = 1) -> RateLimitResult:
        """Check if request is allowed without consuming quota."""
        pass

    @abstractmethod
    def acquire(self, key: str, cost: int = 1) -> RateLimitResult:
        """Acquire quota for a request."""
        pass

    @abstractmethod
    def reset(self, key: str) -> None:
        """Reset quota for a key."""
        pass

    def consume(self, key: str, cost: int = 1, *, tokens: int | None = None) -> RateLimitResult:
        """Consume quota, returning a result instead of raising.

        This is a convenience wrapper around acquire() that catches
        RateLimitExceeded and returns a denied result instead.

        Args:
            key: Rate limit key.
            cost: Number of units to consume.
            tokens: Alias for cost (for token bucket style usage).

        Returns:
            RateLimitResult with allowed=True if successful, or
            allowed=False if the limit was exceeded.
        """
        effective_cost = tokens if tokens is not None else cost
        try:
            return self.acquire(key, effective_cost)
        except RateLimitExceeded as e:
            check_result = self.check(key, effective_cost)
            return RateLimitResult(
                allowed=False,
                remaining=check_result.remaining,
                limit=check_result.limit,
                reset_at=check_result.reset_at,
                retry_after=e.retry_after,
            )


class FixedWindowLimiter(RateLimiter):
    """Fixed window rate limiter."""

    def __init__(self, limit: int, window_seconds: int):
        self.limit = limit
        self.window_seconds = window_seconds
        self._counts: dict[str, tuple[int, datetime]] = {}
        self._lock = threading.Lock()

    def _get_window_start(self) -> datetime:
        """Get current window start time."""
        now = datetime.now()
        seconds = now.timestamp()
        window_start = seconds - (seconds % self.window_seconds)
        return datetime.fromtimestamp(window_start)

    def check(self, key: str, cost: int = 1) -> RateLimitResult:
        """Check without consuming."""
        window_start = self._get_window_start()
        reset_at = window_start + timedelta(seconds=self.window_seconds)

        with self._lock:
            if key in self._counts:
                count, window = self._counts[key]
                if window == window_start:
                    remaining = max(0, self.limit - count)
                    return RateLimitResult(
                        allowed=remaining >= cost,
                        remaining=remaining,
                        limit=self.limit,
                        reset_at=reset_at,
                    )

            return RateLimitResult(
                allowed=True,
                remaining=self.limit,
                limit=self.limit,
                reset_at=reset_at,
            )

    def acquire(self, key: str, cost: int = 1) -> RateLimitResult:
        """Acquire quota."""
        window_start = self._get_window_start()
        reset_at = window_start + timedelta(seconds=self.window_seconds)

        with self._lock:
            if key in self._counts:
                count, window = self._counts[key]
                if window != window_start:
                    count = 0
            else:
                count = 0

            if count + cost > self.limit:
                retry_after = (reset_at - datetime.now()).total_seconds()
                raise RateLimitExceeded(
                    f"Rate limit exceeded for {key}",
                    retry_after=retry_after,
                )

            self._counts[key] = (count + cost, window_start)
            remaining = self.limit - count - cost

            return RateLimitResult(
                allowed=True,
                remaining=remaining,
                limit=self.limit,
                reset_at=reset_at,
            )

    def reset(self, key: str) -> None:
        """Reset quota for key."""
        with self._lock:
            if key in self._counts:
                del self._counts[key]


class SlidingWindowLimiter(RateLimiter):
    """Sliding window rate limiter."""

    def __init__(self, limit: int, window_seconds: int):
        self.limit = limit
        self.window_seconds = window_seconds
        self._requests: dict[str, deque] = {}
        self._lock = threading.Lock()

    def _clean_old_requests(self, key: str, now: float) -> None:
        """Remove expired requests from window."""
        if key not in self._requests:
            return
        cutoff = now - self.window_seconds
        while self._requests[key] and self._requests[key][0] < cutoff:
            self._requests[key].popleft()

    def check(self, key: str, cost: int = 1) -> RateLimitResult:
        """Check without consuming."""
        now = time.time()
        with self._lock:
            self._clean_old_requests(key, now)
            current_count = len(self._requests.get(key, []))
            remaining = max(0, self.limit - current_count)
            return RateLimitResult(
                allowed=remaining >= cost,
                remaining=remaining,
                limit=self.limit,
                reset_at=datetime.fromtimestamp(now + self.window_seconds),
            )

    def acquire(self, key: str, cost: int = 1) -> RateLimitResult:
        """Acquire quota."""
        now = time.time()
        with self._lock:
            if key not in self._requests:
                self._requests[key] = deque()
            self._clean_old_requests(key, now)
            current_count = len(self._requests[key])
            if current_count + cost > self.limit:
                if self._requests[key]:
                    retry_after = self._requests[key][0] + self.window_seconds - now
                else:
                    retry_after = self.window_seconds
                raise RateLimitExceeded(
                    f"Rate limit exceeded for {key}",
                    retry_after=retry_after,
                )
            for _ in range(cost):
                self._requests[key].append(now)
            remaining = self.limit - current_count - cost
            return RateLimitResult(
                allowed=True,
                remaining=remaining,
                limit=self.limit,
                reset_at=datetime.fromtimestamp(now + self.window_seconds),
            )

    def reset(self, key: str) -> None:
        """Reset quota for key."""
        with self._lock:
            if key in self._requests:
                del self._requests[key]


class TokenBucketLimiter(RateLimiter):
    """Token bucket rate limiter."""

    def __init__(
        self,
        capacity: int,
        refill_rate: float,
        refill_interval: float = 1.0,
        initial_tokens: int | None = None,
    ):
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.refill_interval = refill_interval
        self._initial_tokens = initial_tokens if initial_tokens is not None else capacity
        self._buckets: dict[str, tuple[float, float]] = {}
        self._lock = threading.Lock()

    def _get_tokens(self, key: str) -> float:
        """Get current token count for key."""
        now = time.time()
        if key not in self._buckets:
            # Initialize the bucket on first access
            self._buckets[key] = (float(self._initial_tokens), now)
            return float(self._initial_tokens)
        tokens, last_update = self._buckets[key]
        elapsed = now - last_update
        refilled = (elapsed / self.refill_interval) * self.refill_rate
        current = min(self.capacity, tokens + refilled)
        # Update the stored state so future calls see the refill
        self._buckets[key] = (current, now)
        return current

    def check(self, key: str, cost: int = 1) -> RateLimitResult:
        """Check without consuming."""
        with self._lock:
            tokens = self._get_tokens(key)
            return RateLimitResult(
                allowed=tokens >= cost,
                remaining=int(tokens),
                limit=self.capacity,
            )

    def acquire(self, key: str, cost: int = 1) -> RateLimitResult:
        """Acquire tokens."""
        now = time.time()
        with self._lock:
            tokens = self._get_tokens(key)
            if tokens < cost:
                needed = cost - tokens
                retry_after = (needed / self.refill_rate) * self.refill_interval
                raise RateLimitExceeded(
                    f"Rate limit exceeded for {key}",
                    retry_after=retry_after,
                )
            self._buckets[key] = (tokens - cost, now)
            return RateLimitResult(
                allowed=True,
                remaining=int(tokens - cost),
                limit=self.capacity,
            )

    def reset(self, key: str) -> None:
        """Reset bucket for key."""
        with self._lock:
            if key in self._buckets:
                del self._buckets[key]


class CompositeRateLimiter(RateLimiter):
    """Composite rate limiter that enforces multiple limiters simultaneously.

    A request is only allowed if ALL constituent limiters allow it.
    Useful for applying different rate limit policies together
    (e.g., per-second + per-minute + per-hour limits).
    """

    def __init__(self, limiters: dict[str, RateLimiter]):
        """Initialize composite rate limiter.

        Args:
            limiters: Dictionary of name → RateLimiter instances.
        """
        self.limiters = limiters

    def check(self, key: str, cost: int = 1) -> RateLimitResult:
        """Check all limiters without consuming quota.

        Returns the most restrictive result (lowest remaining).
        """
        most_restrictive = None
        for _name, limiter in self.limiters.items():
            result = limiter.check(key, cost)
            if most_restrictive is None or result.remaining < most_restrictive.remaining:
                most_restrictive = result
        if most_restrictive is None:
            return RateLimitResult(allowed=True, remaining=0, limit=0)
        return most_restrictive

    def acquire(self, key: str, cost: int = 1) -> RateLimitResult:
        """Acquire quota from all limiters.

        All limiters must allow the request. If any raises
        RateLimitExceeded, the exception propagates.
        """
        results = []
        for _name, limiter in self.limiters.items():
            results.append(limiter.acquire(key, cost))
        # Return the most restrictive result
        if not results:
            return RateLimitResult(allowed=True, remaining=0, limit=0)
        return min(results, key=lambda r: r.remaining)

    def reset(self, key: str) -> None:
        """Reset all limiters for key."""
        for limiter in self.limiters.values():
            limiter.reset(key)


class RateLimiterMiddleware:
    """Middleware wrapper around any RateLimiter.

    Provides a simplified interface: ``check()`` acquires a token
    and returns a RateLimitResult (instead of raising), while
    ``would_allow()`` inspects without consuming.
    """

    def __init__(self, limiter: RateLimiter):
        self.limiter = limiter

    def check(self, key: str, cost: int = 1) -> RateLimitResult:
        """Acquire quota, returning a result instead of raising."""
        try:
            return self.limiter.acquire(key, cost)
        except RateLimitExceeded:
            result = self.limiter.check(key, cost)
            return RateLimitResult(
                allowed=False,
                remaining=result.remaining,
                limit=result.limit,
                reset_at=result.reset_at,
            )

    def would_allow(self, key: str, cost: int = 1) -> bool:
        """Check whether a request would be allowed without consuming."""
        result = self.limiter.check(key, cost)
        return result.allowed

    def reset(self, key: str) -> None:
        """Reset limiter state for key."""
        self.limiter.reset(key)


def create_rate_limiter(strategy: str, **kwargs) -> RateLimiter:
    """Factory function to create a rate limiter by strategy name.

    Args:
        strategy: One of 'fixed_window', 'sliding_window', 'token_bucket'.
        **kwargs: Strategy-specific parameters.

    Returns:
        Configured RateLimiter instance.

    Raises:
        ValueError: If strategy is not recognized.
    """
    factories = {
        "fixed_window": FixedWindowLimiter,
        "sliding_window": SlidingWindowLimiter,
        "token_bucket": TokenBucketLimiter,
    }
    if strategy not in factories:
        raise ValueError(
            f"Unknown limiter type: {strategy!r}. "
            f"Available: {', '.join(factories)}"
        )
    return factories[strategy](**kwargs)


