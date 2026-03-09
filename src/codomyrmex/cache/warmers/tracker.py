"""AccessTracker and AdaptiveKeyProvider: access-pattern-based key selection."""

import threading
import time
from typing import Generic, TypeVar

from .providers import KeyProvider

K = TypeVar("K")


class AccessTracker(Generic[K]):
    """
    Track cache access patterns for adaptive warming.

    Usage:
        tracker = AccessTracker[str]()
        tracker.record_access("user:1")
        hot_keys = tracker.get_hot_keys(threshold=2)
    """

    def __init__(self, max_keys: int = 10000):
        self.max_keys = max_keys
        self._access_counts: dict[K, int] = {}
        self._last_access: dict[K, float] = {}
        self._lock = threading.Lock()

    def record_access(self, key: K) -> None:
        """Record an access to a key."""
        with self._lock:
            self._access_counts[key] = self._access_counts.get(key, 0) + 1
            self._last_access[key] = time.time()
            if len(self._access_counts) > self.max_keys:
                self._trim()

    def _trim(self) -> None:
        """Evict the oldest half of tracked keys."""
        sorted_by_time = sorted(self._last_access.items(), key=lambda x: x[1])
        for key, _ in sorted_by_time[: len(sorted_by_time) // 2]:
            del self._access_counts[key]
            del self._last_access[key]

    def get_access_count(self, key: K) -> int:
        return self._access_counts.get(key, 0)

    def get_hot_keys(self, threshold: int = 5, limit: int = 100) -> list[K]:
        """Return most-accessed keys exceeding the threshold."""
        with self._lock:
            hot = [(k, c) for k, c in self._access_counts.items() if c >= threshold]
            hot.sort(key=lambda x: x[1], reverse=True)
            return [k for k, _ in hot[:limit]]

    def get_recent_keys(self, seconds: float = 300.0, limit: int = 100) -> list[K]:
        """Return most-recently-accessed keys within the time window."""
        cutoff = time.time() - seconds
        with self._lock:
            recent = [(k, t) for k, t in self._last_access.items() if t >= cutoff]
            recent.sort(key=lambda x: x[1], reverse=True)
            return [k for k, _ in recent[:limit]]

    def clear(self) -> None:
        with self._lock:
            self._access_counts.clear()
            self._last_access.clear()


class AdaptiveKeyProvider(KeyProvider[K]):
    """Key provider that supplies hot keys from an AccessTracker."""

    def __init__(
        self, tracker: AccessTracker[K], threshold: int = 5, limit: int = 1000
    ):
        self.tracker = tracker
        self.threshold = threshold
        self.limit = limit

    def get_keys(self) -> list[K]:
        return self.tracker.get_hot_keys(threshold=self.threshold, limit=self.limit)
