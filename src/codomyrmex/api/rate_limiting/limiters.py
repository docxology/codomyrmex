"""
Rate Limiters

Rate limiter implementations: fixed window, sliding window, token bucket.
"""

import math
import threading
import time
from abc import ABC, abstractmethod
from collections import deque
from collections.abc import Callable
from datetime import datetime, timedelta

from .models import RateLimitExceeded, RateLimitResult


def _validate_cost(cost: int) -> None:
    """Costs count quota units; zero is an explicit no-op."""
    if isinstance(cost, bool) or not isinstance(cost, int) or cost < 0:
        raise ValueError("cost must be a non-negative integer")


def _validate_positive_integer(value: int, name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ValueError(f"{name} must be a positive integer")


class RateLimiter(ABC):
    """Abstract base class for rate limiters."""

    @abstractmethod
    def check(self, key: str, cost: int = 1) -> RateLimitResult:
        """Check if request is allowed without consuming quota."""

    @abstractmethod
    def acquire(self, key: str, cost: int = 1) -> RateLimitResult:
        """Acquire quota for a request."""

    @abstractmethod
    def reset(self, key: str) -> None:
        """Reset quota for a key."""

    def consume(self, key: str, cost: int = 1) -> RateLimitResult:
        """Consume quota, returning a result instead of raising.

        This is a convenience wrapper around acquire() that catches
        RateLimitExceeded and returns a denied result instead.

        Args:
            key: Rate limit key.
            cost: Number of units to consume.
        Returns:
            RateLimitResult with allowed=True if successful, or
            allowed=False if the limit was exceeded.
        """
        try:
            return self.acquire(key, cost)
        except RateLimitExceeded as e:
            check_result = self.check(key, cost)
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
        _validate_positive_integer(limit, "limit")
        _validate_positive_integer(window_seconds, "window_seconds")
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
        _validate_cost(cost)
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
                        retry_after=(reset_at - datetime.now()).total_seconds()
                        if remaining < cost <= self.limit
                        else None,
                    )

            return RateLimitResult(
                allowed=self.limit >= cost,
                remaining=self.limit,
                limit=self.limit,
                reset_at=reset_at,
            )

    def acquire(self, key: str, cost: int = 1) -> RateLimitResult:
        """Acquire quota."""
        _validate_cost(cost)
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

    def __init__(
        self,
        limit: int,
        window_seconds: int,
        *,
        clock: Callable[[], float] = time.monotonic,
    ):
        _validate_positive_integer(limit, "limit")
        _validate_positive_integer(window_seconds, "window_seconds")
        self.limit = limit
        self.window_seconds = window_seconds
        self._clock = clock
        self._requests: dict[str, deque[float]] = {}
        self._lock = threading.Lock()

    def _clean_old_requests(self, key: str, now: float) -> None:
        """Remove expired requests from window."""
        queue = self._requests.get(key)
        if not queue:
            return
        cutoff = now - self.window_seconds
        while queue and queue[0] < cutoff:
            queue.popleft()

    def check(self, key: str, cost: int = 1) -> RateLimitResult:
        """Check without consuming."""
        _validate_cost(cost)
        with self._lock:
            now = self._clock()
            self._clean_old_requests(key, now)
            current_count = len(self._requests.get(key, []))
            remaining = max(0, self.limit - current_count)
            retry_after = None
            if remaining < cost <= self.limit:
                required_expirations = current_count + cost - self.limit
                retry_after = (
                    self._requests[key][required_expirations - 1]
                    + self.window_seconds
                    - now
                )
            return RateLimitResult(
                allowed=remaining >= cost,
                remaining=remaining,
                limit=self.limit,
                reset_at=datetime.now() + timedelta(seconds=self.window_seconds),
                retry_after=retry_after,
            )

    def acquire(self, key: str, cost: int = 1) -> RateLimitResult:
        """Acquire quota."""
        _validate_cost(cost)
        with self._lock:
            now = self._clock()
            if key not in self._requests:
                self._requests[key] = deque()
            self._clean_old_requests(key, now)
            current_count = len(self._requests[key])
            if current_count + cost > self.limit:
                if cost <= self.limit:
                    required_expirations = current_count + cost - self.limit
                    retry_after = (
                        self._requests[key][required_expirations - 1]
                        + self.window_seconds
                        - now
                    )
                else:
                    # No amount of waiting makes a request larger than the
                    # configured quota possible.
                    retry_after = None
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
                reset_at=datetime.now() + timedelta(seconds=self.window_seconds),
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
        *,
        clock: Callable[[], float] = time.monotonic,
    ):
        _validate_positive_integer(capacity, "capacity")
        if not math.isfinite(refill_rate) or refill_rate <= 0:
            raise ValueError("refill_rate must be finite and positive")
        if not math.isfinite(refill_interval) or refill_interval <= 0:
            raise ValueError("refill_interval must be finite and positive")
        if initial_tokens is not None and (
            isinstance(initial_tokens, bool)
            or not isinstance(initial_tokens, int)
            or not 0 <= initial_tokens <= capacity
        ):
            raise ValueError("initial_tokens must be an integer between 0 and capacity")
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.refill_interval = refill_interval
        self._initial_tokens = (
            initial_tokens if initial_tokens is not None else capacity
        )
        self._buckets: dict[str, tuple[float, float]] = {}
        self._clock = clock
        self._lock = threading.Lock()

    def _get_tokens(self, key: str) -> float:
        """Get current token count for key."""
        now = self._clock()
        if key not in self._buckets:
            # Initialize the bucket on first access
            self._buckets[key] = (float(self._initial_tokens), now)
            return float(self._initial_tokens)
        tokens, last_update = self._buckets[key]
        elapsed = max(0.0, now - last_update)
        refilled = (elapsed / self.refill_interval) * self.refill_rate
        current = min(self.capacity, tokens + refilled)
        # Update the stored state so future calls see the refill
        self._buckets[key] = (current, now)
        return current

    def check(self, key: str, cost: int = 1) -> RateLimitResult:
        """Check without consuming."""
        _validate_cost(cost)
        with self._lock:
            tokens = self._get_tokens(key)
            return RateLimitResult(
                allowed=tokens >= cost,
                remaining=int(tokens),
                limit=self.capacity,
                retry_after=((cost - tokens) / self.refill_rate) * self.refill_interval
                if tokens < cost <= self.capacity
                else None,
            )

    def acquire(self, key: str, cost: int = 1) -> RateLimitResult:
        """Acquire tokens."""
        _validate_cost(cost)
        with self._lock:
            tokens = self._get_tokens(key)
            if tokens < cost:
                needed = cost - tokens
                retry_after = (
                    (needed / self.refill_rate) * self.refill_interval
                    if cost <= self.capacity
                    else None
                )
                raise RateLimitExceeded(
                    f"Rate limit exceeded for {key}",
                    retry_after=retry_after,
                )
            self._buckets[key] = (tokens - cost, self._buckets[key][1])
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
        _validate_cost(cost)
        most_restrictive = None
        for limiter in self.limiters.values():
            result = limiter.check(key, cost)
            if (
                most_restrictive is None
                or result.remaining < most_restrictive.remaining
            ):
                most_restrictive = result
        if most_restrictive is None:
            return RateLimitResult(allowed=True, remaining=0, limit=0)
        return most_restrictive

    def acquire(self, key: str, cost: int = 1) -> RateLimitResult:
        """Acquire quota from all limiters.

        Preflight every limiter before consuming. Independent limiters can
        change between check and acquire; this is not a rollback transaction.
        """
        _validate_cost(cost)
        for limiter in self.limiters.values():
            result = limiter.check(key, cost)
            if not result.allowed:
                raise RateLimitExceeded(
                    f"Composite rate limit exceeded for {key}",
                    retry_after=result.retry_after,
                )
        results = []
        for limiter in self.limiters.values():
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
        except RateLimitExceeded as exc:
            result = self.limiter.check(key, cost)
            return RateLimitResult(
                allowed=False,
                remaining=result.remaining,
                limit=result.limit,
                reset_at=result.reset_at,
                retry_after=exc.retry_after,
            )

    def would_allow(self, key: str, cost: int = 1) -> bool:
        """Check whether a request would be allowed without consuming."""
        result = self.limiter.check(key, cost)
        return result.allowed

    def reset(self, key: str) -> None:
        """Reset limiter state for key."""
        self.limiter.reset(key)


_LIMITER_FACTORIES = {
    "fixed_window": FixedWindowLimiter,
    "sliding_window": SlidingWindowLimiter,
    "token_bucket": TokenBucketLimiter,
}


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
    if strategy not in _LIMITER_FACTORIES:
        raise ValueError(
            f"Unknown limiter type: {strategy!r}. Available: {', '.join(_LIMITER_FACTORIES)}"
        )
    return _LIMITER_FACTORIES[strategy](**kwargs)
