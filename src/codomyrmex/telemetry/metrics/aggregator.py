"""Unified metrics aggregation with histograms, labels, and time-windowed stats.

Provides:
- MetricAggregator: local metrics collection (counters, gauges, histograms)
- Label support for multi-dimensional metrics
- Time-windowed counter rates
- Snapshot and summary reporting
"""

from __future__ import annotations

import logging
import math
import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class HistogramBucket:
    """A histogram with configurable bucket boundaries."""

    boundaries: list[float] = field(default_factory=lambda: [0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0])
    counts: list[int] = field(default_factory=list)
    total_count: int = 0
    total_sum: float = 0.0

    def __post_init__(self) -> None:
        if not self.counts:
            self.counts = [0] * (len(self.boundaries) + 1)  # +1 for overflow

    def observe(self, value: float) -> None:
        """Record an observation."""
        self.total_count += 1
        self.total_sum += value
        for i, boundary in enumerate(self.boundaries):
            if value <= boundary:
                self.counts[i] += 1
                return
        self.counts[-1] += 1  # overflow bucket

    @property
    def mean(self) -> float:
        return self.total_sum / max(self.total_count, 1)

    def to_dict(self) -> dict[str, Any]:
        buckets = {f"le_{b}": c for b, c in zip(self.boundaries, self.counts)}
        buckets["le_inf"] = self.counts[-1]
        return {
            "buckets": buckets,
            "count": self.total_count,
            "sum": self.total_sum,
            "mean": round(self.mean, 6),
        }


class MetricAggregator:
    """Aggregates counters, gauges, and histograms locally.

    Supports labels for multi-dimensional metrics and time-windowed rates.

    Example::

        agg = MetricAggregator()
        agg.increment("http_requests", labels={"method": "GET"})
        agg.observe("request_duration", 0.15)
        print(agg.get_snapshot())
    """

    def __init__(self) -> None:
        self._counters: dict[str, float] = {}
        self._gauges: dict[str, float] = {}
        self._histograms: dict[str, HistogramBucket] = {}
        self._labeled_counters: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))
        self._counter_timestamps: dict[str, float] = {}

    def increment(self, name: str, value: float = 1.0, labels: dict[str, str] | None = None) -> None:
        """Increment a counter, optionally with labels."""
        self._counters[name] = self._counters.get(name, 0.0) + value
        if name not in self._counter_timestamps:
            self._counter_timestamps[name] = time.time()
        if labels:
            label_key = ",".join(f"{k}={v}" for k, v in sorted(labels.items()))
            self._labeled_counters[name][label_key] += value

    def set_gauge(self, name: str, value: float) -> None:
        """Set a gauge to a specific value."""
        self._gauges[name] = value

    def observe(self, name: str, value: float) -> None:
        """Record a histogram observation."""
        if name not in self._histograms:
            self._histograms[name] = HistogramBucket()
        self._histograms[name].observe(value)

    def get_counter(self, name: str) -> float:
        return self._counters.get(name, 0.0)

    def get_gauge(self, name: str) -> float:
        return self._gauges.get(name, 0.0)

    def get_histogram(self, name: str) -> HistogramBucket | None:
        return self._histograms.get(name)

    def counter_rate(self, name: str) -> float:
        """Compute the per-second rate of a counter since first increment."""
        total = self._counters.get(name, 0.0)
        first_ts = self._counter_timestamps.get(name)
        if not first_ts or total == 0:
            return 0.0
        elapsed = time.time() - first_ts
        return total / max(elapsed, 0.001)

    def get_snapshot(self) -> dict[str, Any]:
        """Full snapshot of all metrics."""
        return {
            "counters": dict(self._counters),
            "gauges": dict(self._gauges),
            "histograms": {k: v.to_dict() for k, v in self._histograms.items()},
            "timestamp": time.time(),
        }

    def get_labeled_counters(self, name: str) -> dict[str, float]:
        """Get labeled counter breakdowns."""
        return dict(self._labeled_counters.get(name, {}))

    def reset(self) -> None:
        """Reset counters and histograms. Gauges persist."""
        self._counters.clear()
        self._histograms.clear()
        self._labeled_counters.clear()
        self._counter_timestamps.clear()

    def reset_all(self) -> None:
        """Reset everything including gauges."""
        self.reset()
        self._gauges.clear()

    @property
    def metric_names(self) -> list[str]:
        """All registered metric names."""
        names = set(self._counters) | set(self._gauges) | set(self._histograms)
        return sorted(names)

    def summary(self) -> dict[str, Any]:
        return {
            "counters": len(self._counters),
            "gauges": len(self._gauges),
            "histograms": len(self._histograms),
            "total_metrics": len(self.metric_names),
        }
