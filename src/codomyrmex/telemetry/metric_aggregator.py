"""In-process metric aggregation.

Provides counters, gauges, and histograms with configurable
flush intervals for monitoring.
"""

from __future__ import annotations

import math
import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any


@dataclass
class MetricSnapshot:
    """Point-in-time snapshot of all metrics.

    Attributes:
        counters: Counter values.
        gauges: Gauge values.
        histograms: Histogram statistics.
        timestamp: Snapshot creation time.
    """

    counters: dict[str, float] = field(default_factory=dict)
    gauges: dict[str, float] = field(default_factory=dict)
    histograms: dict[str, dict[str, float]] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)


class MetricAggregator:
    """In-process metric collection and aggregation.

    Example::

        metrics = MetricAggregator()
        metrics.increment("requests")
        metrics.gauge("cpu_percent", 65.3)
        metrics.observe("latency_ms", 42.5)
        snap = metrics.snapshot()
    """

    def __init__(self) -> None:
        """Execute   Init   operations natively."""
        self._counters: dict[str, float] = defaultdict(float)
        self._gauges: dict[str, float] = {}
        self._histograms: dict[str, list[float]] = defaultdict(list)

    def increment(self, name: str, value: float = 1.0) -> None:
        """Increment a counter."""
        self._counters[name] += value

    def decrement(self, name: str, value: float = 1.0) -> None:
        """Decrement a counter."""
        self._counters[name] -= value

    def gauge(self, name: str, value: float) -> None:
        """Set a gauge value."""
        self._gauges[name] = value

    def observe(self, name: str, value: float) -> None:
        """Record an observation in a histogram."""
        self._histograms[name].append(value)

    def counter_value(self, name: str) -> float:
        """Get current counter value."""
        return self._counters.get(name, 0.0)

    def gauge_value(self, name: str) -> float | None:
        """Get current gauge value."""
        return self._gauges.get(name)

    def histogram_stats(self, name: str) -> dict[str, float]:
        """Get histogram statistics.

        Returns:
            Dict with count, sum, min, max, mean, p50, p95, p99.
        """
        values = sorted(self._histograms.get(name, []))
        if not values:
            return {}

        n = len(values)
        return {
            "count": n,
            "sum": sum(values),
            "min": values[0],
            "max": values[-1],
            "mean": sum(values) / n,
            "p50": values[n // 2],
            "p95": values[int(n * 0.95)] if n >= 20 else values[-1],
            "p99": values[int(n * 0.99)] if n >= 100 else values[-1],
        }

    def snapshot(self) -> MetricSnapshot:
        """Capture a point-in-time snapshot."""
        histograms = {
            name: self.histogram_stats(name)
            for name in self._histograms
        }
        return MetricSnapshot(
            counters=dict(self._counters),
            gauges=dict(self._gauges),
            histograms=histograms,
        )

    def reset(self) -> None:
        """Reset all metrics."""
        self._counters.clear()
        self._gauges.clear()
        self._histograms.clear()


__all__ = ["MetricAggregator", "MetricSnapshot"]
