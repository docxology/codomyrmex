"""
Distributed Rate Limiting

Rate limiting with Redis backend for distributed systems.
"""

import os
import threading
import time
from dataclasses import dataclass
from typing import Any

from codomyrmex.config_management.defaults import DEFAULT_REDIS_URL

from . import RateLimiter, RateLimitExceeded, RateLimitResult
from codomyrmex.logging_monitoring.core.logger_config import get_logger

logger = get_logger(__name__)


@dataclass
class DistributedRateLimiterConfig:
    """Configuration for distributed rate limiting."""
    redis_url: str = ""

    def __post_init__(self):
        if not self.redis_url:
            self.redis_url = os.getenv("REDIS_URL", DEFAULT_REDIS_URL)
    key_prefix: str = "ratelimit:"
    sync_interval: float = 0.1  # Seconds between syncs


class RedisRateLimiter(RateLimiter):
    """Redis-backed distributed rate limiter.

    Note: Requires redis-py package. Falls back to in-memory if unavailable.
    """

    def __init__(
        self,
        limit: int,
        window_seconds: int,
        redis_client: Any | None = None,
        key_prefix: str = "ratelimit:",
    ):
        self.limit = limit
        self.window_seconds = window_seconds
        self.key_prefix = key_prefix
        self._redis = redis_client
        self._local_cache: dict[str, int] = {}
        self._lock = threading.Lock()

    def _get_key(self, key: str) -> str:
        """Get Redis key with prefix."""
        return f"{self.key_prefix}{key}:{int(time.time()) // self.window_seconds}"

    def check(self, key: str, cost: int = 1) -> RateLimitResult:
        """Check without consuming."""
        if self._redis:
            try:
                redis_key = self._get_key(key)
                current = int(self._redis.get(redis_key) or 0)
                remaining = max(0, self.limit - current)
                return RateLimitResult(
                    allowed=remaining >= cost,
                    remaining=remaining,
                    limit=self.limit,
                )
            except Exception as e:
                logger.warning("Redis check failed, falling back to local limiter: %s", e)

        # Fallback to local
        with self._lock:
            current = self._local_cache.get(key, 0)
            remaining = max(0, self.limit - current)
            return RateLimitResult(
                allowed=remaining >= cost,
                remaining=remaining,
                limit=self.limit,
            )

    def acquire(self, key: str, cost: int = 1) -> RateLimitResult:
        """Acquire quota atomically."""
        if self._redis:
            try:
                redis_key = self._get_key(key)
                pipe = self._redis.pipeline()
                pipe.incr(redis_key, cost)
                pipe.expire(redis_key, self.window_seconds)
                results = pipe.execute()

                current = results[0]
                if current > self.limit:
                    # Over limit, decrement and raise
                    self._redis.decr(redis_key, cost)
                    raise RateLimitExceeded(
                        f"Rate limit exceeded for {key}",
                        retry_after=self.window_seconds,
                    )

                return RateLimitResult(
                    allowed=True,
                    remaining=self.limit - current,
                    limit=self.limit,
                )
            except RateLimitExceeded:
                raise
            except Exception as e:
                logger.warning("Redis acquire failed, falling back to local limiter: %s", e)

        # Fallback to local
        with self._lock:
            current = self._local_cache.get(key, 0)
            if current + cost > self.limit:
                raise RateLimitExceeded(
                    f"Rate limit exceeded for {key}",
                    retry_after=self.window_seconds,
                )

            self._local_cache[key] = current + cost
            return RateLimitResult(
                allowed=True,
                remaining=self.limit - current - cost,
                limit=self.limit,
            )

    def reset(self, key: str) -> None:
        """Reset quota for key."""
        if self._redis:
            try:
                redis_key = self._get_key(key)
                self._redis.delete(redis_key)
            except Exception as e:
                logger.warning("Redis reset failed for key %s: %s", key, e)

        with self._lock:
            self._local_cache.pop(key, None)


class LeakyBucketLimiter(RateLimiter):
    """Leaky bucket rate limiter.

    Smooths burst traffic by processing at a constant rate.
    """

    def __init__(
        self,
        capacity: int,
        leak_rate: float,  # Requests per second
    ):
        self.capacity = capacity
        self.leak_rate = leak_rate
        self._buckets: dict[str, tuple] = {}  # key -> (level, last_update)
        self._lock = threading.Lock()

    def _get_level(self, key: str) -> float:
        """Get current bucket level after leaking."""
        now = time.time()

        if key not in self._buckets:
            return 0.0

        level, last_update = self._buckets[key]
        elapsed = now - last_update
        leaked = elapsed * self.leak_rate

        return max(0, level - leaked)

    def check(self, key: str, cost: int = 1) -> RateLimitResult:
        """Check without consuming."""
        with self._lock:
            level = self._get_level(key)
            space = self.capacity - level

            return RateLimitResult(
                allowed=space >= cost,
                remaining=int(space),
                limit=self.capacity,
            )

    def acquire(self, key: str, cost: int = 1) -> RateLimitResult:
        """Add to bucket."""
        now = time.time()

        with self._lock:
            level = self._get_level(key)

            if level + cost > self.capacity:
                # Calculate when space will be available
                excess = level + cost - self.capacity
                retry_after = excess / self.leak_rate

                raise RateLimitExceeded(
                    f"Bucket full for {key}",
                    retry_after=retry_after,
                )

            self._buckets[key] = (level + cost, now)

            return RateLimitResult(
                allowed=True,
                remaining=int(self.capacity - level - cost),
                limit=self.capacity,
            )

    def reset(self, key: str) -> None:
        """Empty the bucket."""
        with self._lock:
            self._buckets.pop(key, None)


class AdaptiveRateLimiter(RateLimiter):
    """Adaptive rate limiter that adjusts based on system load.

    Automatically reduces limits during high load periods.
    """

    def __init__(
        self,
        base_limit: int,
        window_seconds: int,
        load_threshold: float = 0.8,
        min_limit_ratio: float = 0.2,
    ):
        self.base_limit = base_limit
        self.window_seconds = window_seconds
        self.load_threshold = load_threshold
        self.min_limit_ratio = min_limit_ratio

        self._current_load = 0.0
        self._request_counts: dict[str, list] = {}
        self._lock = threading.Lock()

    def _effective_limit(self) -> int:
        """Get current effective limit based on load."""
        if self._current_load <= self.load_threshold:
            return self.base_limit

        # Reduce limit linearly as load increases
        load_factor = 1 - ((self._current_load - self.load_threshold) / (1 - self.load_threshold))
        load_factor = max(self.min_limit_ratio, load_factor)

        return int(self.base_limit * load_factor)

    def set_load(self, load: float) -> None:
        """Update current system load (0-1)."""
        self._current_load = max(0, min(1, load))

    def _clean_old_requests(self, key: str) -> None:
        """Remove old request timestamps."""
        now = time.time()
        cutoff = now - self.window_seconds

        if key in self._request_counts:
            self._request_counts[key] = [
                t for t in self._request_counts[key] if t > cutoff
            ]

    def check(self, key: str, cost: int = 1) -> RateLimitResult:
        """Check without consuming."""
        with self._lock:
            self._clean_old_requests(key)
            current = len(self._request_counts.get(key, []))
            limit = self._effective_limit()
            remaining = max(0, limit - current)

            return RateLimitResult(
                allowed=remaining >= cost,
                remaining=remaining,
                limit=limit,
            )

    def acquire(self, key: str, cost: int = 1) -> RateLimitResult:
        """Acquire with adaptive limits."""
        now = time.time()

        with self._lock:
            self._clean_old_requests(key)

            if key not in self._request_counts:
                self._request_counts[key] = []

            current = len(self._request_counts[key])
            limit = self._effective_limit()

            if current + cost > limit:
                raise RateLimitExceeded(
                    f"Adaptive rate limit exceeded for {key}",
                    retry_after=self.window_seconds,
                )

            for _ in range(cost):
                self._request_counts[key].append(now)

            return RateLimitResult(
                allowed=True,
                remaining=limit - current - cost,
                limit=limit,
            )

    def reset(self, key: str) -> None:
        """Reset quota."""
        with self._lock:
            self._request_counts.pop(key, None)
