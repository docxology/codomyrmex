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
    ):
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.refill_interval = refill_interval
        self._buckets: dict[str, tuple[float, float]] = {}
        self._lock = threading.Lock()

    def _get_tokens(self, key: str) -> float:
        """Get current token count for key."""
        now = time.time()
        if key not in self._buckets:
            return float(self.capacity)
        tokens, last_update = self._buckets[key]
        elapsed = now - last_update
        refilled = (elapsed / self.refill_interval) * self.refill_rate
        return min(self.capacity, tokens + refilled)

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
