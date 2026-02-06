"""
Telemetry Metrics Module

Metrics collection and aggregation.
"""

__version__ = "0.1.0"

import statistics
import threading
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional
from collections.abc import Callable


class MetricType(Enum):
    """Types of metrics."""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"
    TIMER = "timer"


@dataclass
class MetricSample:
    """A single metric sample."""
    value: float
    timestamp: datetime = field(default_factory=datetime.now)
    labels: dict[str, str] = field(default_factory=dict)


@dataclass
class MetricDescriptor:
    """Describes a metric."""
    name: str
    metric_type: MetricType
    description: str = ""
    labels: list[str] = field(default_factory=list)
    unit: str = ""


class Metric(ABC):
    """Base class for metrics."""

    def __init__(self, name: str, description: str = "", labels: list[str] | None = None):
        self.name = name
        self.description = description
        self.allowed_labels = labels or []
        self._lock = threading.Lock()

    @property
    @abstractmethod
    def metric_type(self) -> MetricType:
        """Get metric type."""
        pass

    @abstractmethod
    def get_value(self, labels: dict[str, str] | None = None) -> Any:
        """Get current value."""
        pass


class Counter(Metric):
    """Counter metric (only increases)."""

    def __init__(self, name: str, description: str = "", labels: list[str] | None = None):
        super().__init__(name, description, labels)
        self._values: dict[str, float] = {}

    @property
    def metric_type(self) -> MetricType:
        return MetricType.COUNTER

    def _key(self, labels: dict[str, str] | None) -> str:
        if not labels:
            return ""
        return "|".join(f"{k}={v}" for k, v in sorted(labels.items()))

    def inc(self, value: float = 1.0, labels: dict[str, str] | None = None) -> None:
        """Increment the counter."""
        key = self._key(labels)
        with self._lock:
            self._values[key] = self._values.get(key, 0) + value

    def get_value(self, labels: dict[str, str] | None = None) -> float:
        """Get counter value."""
        key = self._key(labels)
        return self._values.get(key, 0)


class Gauge(Metric):
    """Gauge metric (can go up and down)."""

    def __init__(self, name: str, description: str = "", labels: list[str] | None = None):
        super().__init__(name, description, labels)
        self._values: dict[str, float] = {}

    @property
    def metric_type(self) -> MetricType:
        return MetricType.GAUGE

    def _key(self, labels: dict[str, str] | None) -> str:
        if not labels:
            return ""
        return "|".join(f"{k}={v}" for k, v in sorted(labels.items()))

    def set(self, value: float, labels: dict[str, str] | None = None) -> None:
        """Set the gauge value."""
        key = self._key(labels)
        with self._lock:
            self._values[key] = value

    def inc(self, value: float = 1.0, labels: dict[str, str] | None = None) -> None:
        """Increment the gauge."""
        key = self._key(labels)
        with self._lock:
            self._values[key] = self._values.get(key, 0) + value

    def dec(self, value: float = 1.0, labels: dict[str, str] | None = None) -> None:
        """Decrement the gauge."""
        self.inc(-value, labels)

    def get_value(self, labels: dict[str, str] | None = None) -> float:
        """Get gauge value."""
        key = self._key(labels)
        return self._values.get(key, 0)


class Histogram(Metric):
    """Histogram metric for distributions."""

    DEFAULT_BUCKETS = [0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]

    def __init__(
        self,
        name: str,
        description: str = "",
        labels: list[str] | None = None,
        buckets: list[float] | None = None,
    ):
        super().__init__(name, description, labels)
        self.buckets = sorted(buckets or self.DEFAULT_BUCKETS)
        self._observations: list[float] = []
        self._bucket_counts: dict[float, int] = {b: 0 for b in self.buckets}

    @property
    def metric_type(self) -> MetricType:
        return MetricType.HISTOGRAM

    def observe(self, value: float) -> None:
        """Observe a value."""
        with self._lock:
            self._observations.append(value)
            for bucket in self.buckets:
                if value <= bucket:
                    self._bucket_counts[bucket] += 1

    def get_value(self, labels: dict[str, str] | None = None) -> dict[str, Any]:
        """Get histogram stats."""
        with self._lock:
            if not self._observations:
                return {"count": 0, "sum": 0, "buckets": self._bucket_counts}

            return {
                "count": len(self._observations),
                "sum": sum(self._observations),
                "min": min(self._observations),
                "max": max(self._observations),
                "mean": statistics.mean(self._observations),
                "buckets": dict(self._bucket_counts),
            }


class Summary(Metric):
    """Summary metric with quantiles."""

    DEFAULT_QUANTILES = [0.5, 0.9, 0.95, 0.99]

    def __init__(
        self,
        name: str,
        description: str = "",
        labels: list[str] | None = None,
        quantiles: list[float] | None = None,
    ):
        super().__init__(name, description, labels)
        self.quantiles = quantiles or self.DEFAULT_QUANTILES
        self._observations: list[float] = []

    @property
    def metric_type(self) -> MetricType:
        return MetricType.SUMMARY

    def observe(self, value: float) -> None:
        """Observe a value."""
        with self._lock:
            self._observations.append(value)

    def get_value(self, labels: dict[str, str] | None = None) -> dict[str, Any]:
        """Get summary stats with quantiles."""
        with self._lock:
            if not self._observations:
                return {"count": 0, "sum": 0, "quantiles": {}}

            sorted_obs = sorted(self._observations)
            quantile_values = {}

            for q in self.quantiles:
                idx = int(len(sorted_obs) * q)
                idx = min(idx, len(sorted_obs) - 1)
                quantile_values[q] = sorted_obs[idx]

            return {
                "count": len(self._observations),
                "sum": sum(self._observations),
                "quantiles": quantile_values,
            }


class Timer:
    """Context manager for timing operations."""

    def __init__(self, histogram: Histogram):
        self.histogram = histogram
        self._start: float = 0

    def __enter__(self):
        self._start = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self._start
        self.histogram.observe(duration)


class MetricsRegistry:
    """
    Registry for metrics.

    Usage:
        registry = MetricsRegistry()

        # Create metrics
        requests = registry.counter("http_requests", "Total requests")
        latency = registry.histogram("http_latency", "Request latency")

        # Record values
        requests.inc()
        latency.observe(0.125)

        # Get all metrics
        for name, value in registry.collect():
            print(f"{name}: {value}")
    """

    def __init__(self):
        self._metrics: dict[str, Metric] = {}
        self._lock = threading.Lock()

    def counter(self, name: str, description: str = "", labels: list[str] | None = None) -> Counter:
        """Create or get a counter."""
        with self._lock:
            if name not in self._metrics:
                self._metrics[name] = Counter(name, description, labels)
            return self._metrics[name]

    def gauge(self, name: str, description: str = "", labels: list[str] | None = None) -> Gauge:
        """Create or get a gauge."""
        with self._lock:
            if name not in self._metrics:
                self._metrics[name] = Gauge(name, description, labels)
            return self._metrics[name]

    def histogram(
        self,
        name: str,
        description: str = "",
        labels: list[str] | None = None,
        buckets: list[float] | None = None,
    ) -> Histogram:
        """Create or get a histogram."""
        with self._lock:
            if name not in self._metrics:
                self._metrics[name] = Histogram(name, description, labels, buckets)
            return self._metrics[name]

    def summary(
        self,
        name: str,
        description: str = "",
        labels: list[str] | None = None,
        quantiles: list[float] | None = None,
    ) -> Summary:
        """Create or get a summary."""
        with self._lock:
            if name not in self._metrics:
                self._metrics[name] = Summary(name, description, labels, quantiles)
            return self._metrics[name]

    def collect(self) -> list[tuple]:
        """Collect all metric values."""
        results = []
        for name, metric in self._metrics.items():
            results.append((name, metric.get_value()))
        return results

    def get(self, name: str) -> Metric | None:
        """Get a metric by name."""
        return self._metrics.get(name)


__all__ = [
    # Enums
    "MetricType",
    # Data classes
    "MetricSample",
    "MetricDescriptor",
    # Metrics
    "Metric",
    "Counter",
    "Gauge",
    "Histogram",
    "Summary",
    "Timer",
    # Core
    "MetricsRegistry",
]
