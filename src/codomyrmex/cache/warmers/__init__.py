"""
Cache Warmers Module

Cache pre-population and warming strategies.
"""

__version__ = "0.1.0"

import concurrent.futures
import logging
import threading
import time
from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, Generic, List, Optional, Set, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar('T')
K = TypeVar('K')
V = TypeVar('V')


class WarmingStrategy(Enum):
    """Cache warming strategies."""
    EAGER = "eager"           # Warm all keys at startup
    LAZY = "lazy"             # Warm on first access
    SCHEDULED = "scheduled"   # Warm on schedule
    ADAPTIVE = "adaptive"     # Warm based on access patterns


@dataclass
class WarmingConfig:
    """Configuration for cache warming."""
    strategy: WarmingStrategy = WarmingStrategy.LAZY
    batch_size: int = 100
    max_workers: int = 4
    refresh_interval_s: float = 300.0  # 5 minutes
    warmup_timeout_s: float = 60.0
    retry_on_failure: bool = True
    max_retries: int = 3


@dataclass
class WarmingStats:
    """Statistics for cache warming."""
    keys_warmed: int = 0
    keys_failed: int = 0
    total_time_ms: float = 0.0
    last_warming: datetime | None = None
    errors: list[str] = field(default_factory=list)

    @property
    def success_rate(self) -> float:
        """Calculate success rate."""
        total = self.keys_warmed + self.keys_failed
        if total > 0:
            return self.keys_warmed / total
        return 1.0


class KeyProvider(ABC, Generic[K]):
    """Base class for providing keys to warm."""

    @abstractmethod
    def get_keys(self) -> list[K]:
        """Get list of keys to warm."""
        pass


class StaticKeyProvider(KeyProvider[K]):
    """Provide a static list of keys."""

    def __init__(self, keys: list[K]):
        """Initialize this instance."""
        self._keys = keys

    def get_keys(self) -> list[K]:
        """get Keys ."""
        return self._keys.copy()


class CallableKeyProvider(KeyProvider[K]):
    """Provide keys from a callable."""

    def __init__(self, func: Callable[[], list[K]]):
        """Initialize this instance."""
        self._func = func

    def get_keys(self) -> list[K]:
        """get Keys ."""
        return self._func()


class ValueLoader(ABC, Generic[K, V]):
    """Base class for loading values for cache warming."""

    @abstractmethod
    def load(self, key: K) -> V:
        """Load a value for a given key."""
        pass


class CallableValueLoader(ValueLoader[K, V]):
    """Load values using a callable."""

    def __init__(self, func: Callable[[K], V]):
        """Initialize this instance."""
        self._func = func

    def load(self, key: K) -> V:
        """Load data from the specified source."""
        return self._func(key)


class BatchValueLoader(ValueLoader[K, V]):
    """
    Load values in batches for efficiency.

    The batch function should accept a list of keys and return
    a dict mapping keys to values.
    """

    def __init__(self, batch_func: Callable[[list[K]], dict[K, V]]):
        """Initialize this instance."""
        self._batch_func = batch_func
        self._cache: dict[K, V] = {}

    def load_batch(self, keys: list[K]) -> dict[K, V]:
        """Load a batch of values."""
        result = self._batch_func(keys)
        self._cache.update(result)
        return result

    def load(self, key: K) -> V:
        """Load a single value (uses cache if available)."""
        if key in self._cache:
            return self._cache[key]
        result = self._batch_func([key])
        return result.get(key)  # type: ignore


class CacheWarmer(Generic[K, V]):
    """
    Cache warmer for pre-populating caches.

    Usage:
        # Define key provider and value loader
        keys = StaticKeyProvider(["user:1", "user:2", "user:3"])
        loader = CallableValueLoader(lambda k: fetch_user(k))

        # Create warmer
        warmer = CacheWarmer(
            cache=my_cache,
            key_provider=keys,
            value_loader=loader,
        )

        # Warm the cache
        stats = warmer.warm()
        print(f"Warmed {stats.keys_warmed} keys")

        # Or warm asynchronously
        warmer.warm_async()
    """

    def __init__(
        self,
        cache: dict[K, V],
        key_provider: KeyProvider[K],
        value_loader: ValueLoader[K, V],
        config: WarmingConfig | None = None,
    ):
        """Initialize this instance."""
        self.cache = cache
        self.key_provider = key_provider
        self.value_loader = value_loader
        self.config = config or WarmingConfig()
        self._stats = WarmingStats()
        self._warming = False
        self._lock = threading.Lock()
        self._scheduler_thread: threading.Thread | None = None
        self._stop_scheduler = threading.Event()

    @property
    def stats(self) -> WarmingStats:
        """Get warming statistics."""
        return self._stats

    @property
    def is_warming(self) -> bool:
        """Check if warming is in progress."""
        return self._warming

    def warm(self, keys: list[K] | None = None) -> WarmingStats:
        """
        Warm the cache synchronously.

        Args:
            keys: Specific keys to warm (or all from provider)

        Returns:
            WarmingStats with results
        """
        with self._lock:
            if self._warming:
                return self._stats
            self._warming = True

        start_time = time.time()
        stats = WarmingStats()

        try:
            target_keys = keys if keys is not None else self.key_provider.get_keys()

            # Check if we're using batch loader
            if isinstance(self.value_loader, BatchValueLoader):
                stats = self._warm_batch(target_keys)
            else:
                stats = self._warm_parallel(target_keys)

            stats.total_time_ms = (time.time() - start_time) * 1000
            stats.last_warming = datetime.now()

        finally:
            with self._lock:
                self._warming = False
                self._stats = stats

        return stats

    def _warm_batch(self, keys: list[K]) -> WarmingStats:
        """Warm using batch loading."""
        stats = WarmingStats()
        loader = self.value_loader

        if not isinstance(loader, BatchValueLoader):
            return stats

        # Process in batches
        for i in range(0, len(keys), self.config.batch_size):
            batch = keys[i:i + self.config.batch_size]
            try:
                results = loader.load_batch(batch)
                for key, value in results.items():
                    self.cache[key] = value
                    stats.keys_warmed += 1
            except Exception as e:
                stats.keys_failed += len(batch)
                stats.errors.append(str(e))

        return stats

    def _warm_parallel(self, keys: list[K]) -> WarmingStats:
        """Warm using parallel loading."""
        stats = WarmingStats()

        def load_key(key: K) -> tuple:
            """load Key ."""
            for attempt in range(self.config.max_retries + 1):
                try:
                    value = self.value_loader.load(key)
                    return (key, value, None)
                except Exception as e:
                    if attempt == self.config.max_retries or not self.config.retry_on_failure:
                        return (key, None, str(e))
                    time.sleep(0.1 * (2 ** attempt))  # Exponential backoff
            return (key, None, "Max retries exceeded")

        with concurrent.futures.ThreadPoolExecutor(
            max_workers=self.config.max_workers
        ) as executor:
            futures = {executor.submit(load_key, key): key for key in keys}

            for future in concurrent.futures.as_completed(
                futures,
                timeout=self.config.warmup_timeout_s
            ):
                key, value, error = future.result()
                if error:
                    stats.keys_failed += 1
                    stats.errors.append(f"{key}: {error}")
                else:
                    self.cache[key] = value
                    stats.keys_warmed += 1

        return stats

    def warm_async(self, keys: list[K] | None = None) -> concurrent.futures.Future:
        """
        Warm the cache asynchronously.

        Returns:
            Future that resolves to WarmingStats
        """
        executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        return executor.submit(self.warm, keys)

    def warm_key(self, key: K) -> bool:
        """
        Warm a single key.

        Returns:
            True if successful
        """
        try:
            value = self.value_loader.load(key)
            self.cache[key] = value
            return True
        except Exception as e:
            logger.warning("Failed to warm cache key %r: %s", key, e)
            return False

    def start_scheduler(self) -> None:
        """Start scheduled warming."""
        if self._scheduler_thread and self._scheduler_thread.is_alive():
            return

        self._stop_scheduler.clear()

        def scheduler_loop():
            """scheduler Loop ."""
            while not self._stop_scheduler.wait(self.config.refresh_interval_s):
                self.warm()

        self._scheduler_thread = threading.Thread(target=scheduler_loop, daemon=True)
        self._scheduler_thread.start()

    def stop_scheduler(self) -> None:
        """Stop scheduled warming."""
        self._stop_scheduler.set()
        if self._scheduler_thread:
            self._scheduler_thread.join(timeout=5.0)


class AccessTracker(Generic[K]):
    """
    Track cache access patterns for adaptive warming.

    Usage:
        tracker = AccessTracker[str]()

        # Record accesses
        tracker.record_access("user:1")
        tracker.record_access("user:2")
        tracker.record_access("user:1")

        # Get frequently accessed keys
        hot_keys = tracker.get_hot_keys(threshold=2)
    """

    def __init__(self, max_keys: int = 10000):
        """Initialize this instance."""
        self.max_keys = max_keys
        self._access_counts: dict[K, int] = {}
        self._last_access: dict[K, float] = {}
        self._lock = threading.Lock()

    def record_access(self, key: K) -> None:
        """Record an access to a key."""
        with self._lock:
            self._access_counts[key] = self._access_counts.get(key, 0) + 1
            self._last_access[key] = time.time()

            # Trim if over limit
            if len(self._access_counts) > self.max_keys:
                self._trim()

    def _trim(self) -> None:
        """Trim old or infrequent keys."""
        # Remove oldest half
        sorted_by_time = sorted(
            self._last_access.items(),
            key=lambda x: x[1]
        )
        to_remove = [k for k, _ in sorted_by_time[:len(sorted_by_time) // 2]]

        for key in to_remove:
            del self._access_counts[key]
            del self._last_access[key]

    def get_access_count(self, key: K) -> int:
        """Get access count for a key."""
        return self._access_counts.get(key, 0)

    def get_hot_keys(
        self,
        threshold: int = 5,
        limit: int = 100,
    ) -> list[K]:
        """Get frequently accessed keys."""
        with self._lock:
            hot = [
                (k, count) for k, count in self._access_counts.items()
                if count >= threshold
            ]
            hot.sort(key=lambda x: x[1], reverse=True)
            return [k for k, _ in hot[:limit]]

    def get_recent_keys(
        self,
        seconds: float = 300.0,
        limit: int = 100,
    ) -> list[K]:
        """Get recently accessed keys."""
        cutoff = time.time() - seconds
        with self._lock:
            recent = [
                (k, t) for k, t in self._last_access.items()
                if t >= cutoff
            ]
            recent.sort(key=lambda x: x[1], reverse=True)
            return [k for k, _ in recent[:limit]]

    def clear(self) -> None:
        """Clear all tracking data."""
        with self._lock:
            self._access_counts.clear()
            self._last_access.clear()


class AdaptiveKeyProvider(KeyProvider[K]):
    """
    Key provider based on access patterns.

    Uses an AccessTracker to provide frequently accessed keys.
    """

    def __init__(
        self,
        tracker: AccessTracker[K],
        threshold: int = 5,
        limit: int = 1000,
    ):
        """Initialize this instance."""
        self.tracker = tracker
        self.threshold = threshold
        self.limit = limit

    def get_keys(self) -> list[K]:
        """get Keys ."""
        return self.tracker.get_hot_keys(
            threshold=self.threshold,
            limit=self.limit,
        )


__all__ = [
    # Enums
    "WarmingStrategy",
    # Data classes
    "WarmingConfig",
    "WarmingStats",
    # Key providers
    "KeyProvider",
    "StaticKeyProvider",
    "CallableKeyProvider",
    "AdaptiveKeyProvider",
    # Value loaders
    "ValueLoader",
    "CallableValueLoader",
    "BatchValueLoader",
    # Main classes
    "CacheWarmer",
    "AccessTracker",
]
