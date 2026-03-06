"""Async-native rate limiting for concurrent operations.

Provides token bucket and sliding window rate limiters
designed for use in asyncio contexts.
"""

import asyncio
import time
from dataclasses import dataclass

__all__ = ["AsyncSlidingWindow", "AsyncTokenBucket", "RateLimitConfig"]


@dataclass
class RateLimitConfig:
    """Configuration for rate limiting.

    Attributes:
        max_requests: Maximum number of requests allowed.
        window_seconds: Time window in seconds.
        burst_size: Allowed burst size.
    """

    max_requests: int = 10
    window_seconds: float = 1.0
    burst_size: int | None = None


class AsyncTokenBucket:
    """Token bucket rate limiter for async contexts.

    Allows bursts up to bucket capacity while maintaining
    a sustained rate over time.
    """

    def __init__(self, rate: float, capacity: int | None = None) -> None:
        """Initialize rate limiter.

        Args:
            rate: Fill rate in tokens per second.
            capacity: Maximum bucket size. Defaults to int(rate).

        Example:
            >>> limiter = AsyncTokenBucket(rate=5, capacity=10)
        """
        self._rate = rate
        self._capacity = capacity or int(rate)
        self._tokens = float(self._capacity)
        self._last_refill = time.monotonic()
        self._lock = asyncio.Lock()

    async def acquire(self, tokens: int = 1, timeout: float | None = None) -> bool:
        """Acquire tokens, waiting if necessary.

        Args:
            tokens: Number of tokens to acquire.
            timeout: Maximum time to wait in seconds.

        Returns:
            True if acquired, False if timeout reached.

        Example:
            >>> if await limiter.acquire(1, timeout=2.0):
            ...     pass
        """
        deadline = time.monotonic() + timeout if timeout else None
        while True:
            async with self._lock:
                self._refill()
                if self._tokens >= tokens:
                    self._tokens -= tokens
                    return True
            if deadline and time.monotonic() >= deadline:
                return False
            wait_time = (tokens - self._tokens) / self._rate
            await asyncio.sleep(min(wait_time, 0.1))

    def _refill(self) -> None:
        """Refill the bucket based on elapsed time."""
        now = time.monotonic()
        elapsed = now - self._last_refill
        self._tokens = min(self._capacity, self._tokens + elapsed * self._rate)
        self._last_refill = now


class AsyncSlidingWindow:
    """Sliding window rate limiter for async contexts."""

    def __init__(self, max_requests: int, window_seconds: float) -> None:
        """Initialize sliding window rate limiter.

        Args:
            max_requests: Number of requests allowed per window.
            window_seconds: Sliding window size in seconds.

        Example:
            >>> limiter = AsyncSlidingWindow(max_requests=100, window_seconds=60)
        """
        self._max_requests = max_requests
        self._window = window_seconds
        self._timestamps: list[float] = []
        self._lock = asyncio.Lock()

    async def acquire(self, timeout: float | None = None) -> bool:
        """Check if request is allowed under the sliding window.

        Args:
            timeout: Maximum time to wait in seconds.

        Returns:
            True if acquired, False if timeout reached.

        Example:
            >>> if await limiter.acquire(timeout=0.5):
            ...     pass
        """
        deadline = time.monotonic() + timeout if timeout else None
        while True:
            async with self._lock:
                now = time.monotonic()
                self._timestamps = [
                    t for t in self._timestamps if now - t < self._window
                ]
                if len(self._timestamps) < self._max_requests:
                    self._timestamps.append(now)
                    return True
            if deadline and time.monotonic() >= deadline:
                return False
            await asyncio.sleep(0.05)
