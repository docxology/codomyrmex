"""Cache statistics with time-windowed tracking and eviction metrics.

Provides:
- CacheStats: counters for hits, misses, evictions, memory usage
- Time-windowed hit rate calculation
- Per-key access frequency tracking
- Reset, snapshot, and text/dict reporting
"""

from __future__ import annotations

import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any

from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


@dataclass
class CacheStats:
    """Comprehensive cache statistics.

    Example::

        stats = CacheStats(max_size=1000)
        stats.record_hit("key1")
        stats.record_miss("key2")
        print(stats.hit_rate)
    """

    hits: int = 0
    misses: int = 0
    total_requests: int = 0
    size: int = 0
    max_size: int = 0
    evictions: int = 0
    writes: int = 0
    deletes: int = 0
    _timestamps: list[tuple[float, bool]] = field(default_factory=list, repr=False)
    _key_hits: dict[str, int] = field(default_factory=lambda: defaultdict(int), repr=False)

    @property
    def hit_rate(self) -> float:
        """Overall hit rate (0.0–1.0)."""
        if self.total_requests == 0:
            return 0.0
        return self.hits / self.total_requests

    @property
    def miss_rate(self) -> float:
        """Execute Miss Rate operations natively."""
        if self.total_requests == 0:
            return 0.0
        return self.misses / self.total_requests

    @property
    def usage_percent(self) -> float:
        """Execute Usage Percent operations natively."""
        if self.max_size == 0:
            return 0.0
        return (self.size / self.max_size) * 100

    @property
    def eviction_rate(self) -> float:
        """Evictions as a fraction of total writes."""
        if self.writes == 0:
            return 0.0
        return self.evictions / self.writes

    # ── Recording ───────────────────────────────────────────────────

    def record_hit(self, key: str = "") -> None:
        """Record a cache hit."""
        self.hits += 1
        self.total_requests += 1
        self._timestamps.append((time.time(), True))
        if key:
            self._key_hits[key] += 1

    def record_miss(self, key: str = "") -> None:
        """Record a cache miss."""
        self.misses += 1
        self.total_requests += 1
        self._timestamps.append((time.time(), False))

    def record_write(self) -> None:
        """Execute Record Write operations natively."""
        self.writes += 1

    def record_eviction(self) -> None:
        """Execute Record Eviction operations natively."""
        self.evictions += 1

    def record_delete(self) -> None:
        """Execute Record Delete operations natively."""
        self.deletes += 1

    # ── Time-windowed ───────────────────────────────────────────────

    def hit_rate_window(self, seconds: float = 60.0) -> float:
        """Hit rate within the last N seconds."""
        cutoff = time.time() - seconds
        recent = [(ts, hit) for ts, hit in self._timestamps if ts >= cutoff]
        if not recent:
            return 0.0
        hits = sum(1 for _, hit in recent if hit)
        return hits / len(recent)

    # ── Key frequency ───────────────────────────────────────────────

    def hottest_keys(self, n: int = 10) -> list[tuple[str, int]]:
        """Return top-N most frequently hit keys."""
        return sorted(self._key_hits.items(), key=lambda x: x[1], reverse=True)[:n]

    # ── Output ──────────────────────────────────────────────────────

    def reset(self) -> None:
        """Reset all statistics."""
        self.hits = self.misses = self.total_requests = 0
        self.size = self.evictions = self.writes = self.deletes = 0
        self._timestamps.clear()
        self._key_hits.clear()

    def snapshot(self) -> CacheStats:
        """Create a frozen copy of current stats."""
        return CacheStats(
            hits=self.hits, misses=self.misses, total_requests=self.total_requests,
            size=self.size, max_size=self.max_size, evictions=self.evictions,
            writes=self.writes, deletes=self.deletes,
        )

    def to_dict(self) -> dict[str, Any]:
        """Execute To Dict operations natively."""
        return {
            "hits": self.hits,
            "misses": self.misses,
            "total_requests": self.total_requests,
            "hit_rate": round(self.hit_rate, 4),
            "size": self.size,
            "max_size": self.max_size,
            "usage_percent": round(self.usage_percent, 1),
            "evictions": self.evictions,
            "writes": self.writes,
            "deletes": self.deletes,
        }

    def text(self) -> str:
        """Human-readable summary."""
        return (
            f"Cache: {self.hits}/{self.total_requests} hits "
            f"({self.hit_rate:.1%}), "
            f"{self.size}/{self.max_size} entries, "
            f"{self.evictions} evictions"
        )
