"""
Telemetry Metrics Module

Metrics collection and aggregation.
"""

__version__ = "0.1.0"

import statistics
import threading
import time
from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional


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

    def __init__(self, name: str, description: str = "", labels: dict[str, str] | list[str] | None = None, value: float = 0.0):
        allowed = labels
        if isinstance(labels, dict):
            allowed = list(labels.keys())
        super().__init__(name, description, allowed)
        self._values: dict[str, float] = {"": value}
        if isinstance(labels, dict):
            self.labels = labels
            self._values[self._key(labels)] = value
        else:
            self.labels = {}

    @property
    def metric_type(self) -> MetricType:
        return MetricType.COUNTER

    def _key(self, labels: dict[str, str] | None) -> str:
        """key ."""
        if not labels:
            return ""
        return "|".join(f"{k}={v}" for k, v in sorted(labels.items()))

    def inc(self, value: float = 1.0, labels: dict[str, str] | None = None) -> None:
        """Increment the counter."""
        key = self._key(labels or self.labels)
        with self._lock:
            self._values[key] = self._values.get(key, 0.0) + value

    def get(self, labels: dict[str, str] | None = None) -> float:
        """Get counter value."""
        return self.get_value(labels)

    def get_value(self, labels: dict[str, str] | None = None) -> float:
        """Get counter value."""
        key = self._key(labels or self.labels)
        return self._values.get(key, 0.0)

    @property
    def value(self) -> float:
        """value ."""
        return self.get_value()

class Gauge(Metric):
    """Gauge metric (can go up and down)."""

    def __init__(self, name: str, description: str = "", labels: dict[str, str] | list[str] | None = None, value: float = 0.0):
        allowed = labels
        if isinstance(labels, dict):
            allowed = list(labels.keys())
        super().__init__(name, description, allowed)
        self._values: dict[str, float] = {"": value}
        if isinstance(labels, dict):
            self.labels = labels
            self._values[self._key(labels)] = value
        else:
            self.labels = {}

    @property
    def metric_type(self) -> MetricType:
        return MetricType.GAUGE

    def _key(self, labels: dict[str, str] | None) -> str:
        """key ."""
        if not labels:
            return ""
        return "|".join(f"{k}={v}" for k, v in sorted(labels.items()))

    def set(self, value: float, labels: dict[str, str] | None = None) -> None:
        """Set the gauge value."""
        key = self._key(labels or self.labels)
        with self._lock:
            self._values[key] = value

    def inc(self, value: float = 1.0, labels: dict[str, str] | None = None) -> None:
        """Increment the gauge."""
        key = self._key(labels or self.labels)
        with self._lock:
            self._values[key] = self._values.get(key, 0.0) + value

    def dec(self, value: float = 1.0, labels: dict[str, str] | None = None) -> None:
        """Decrement the gauge."""
        self.inc(-value, labels)

    def get(self, labels: dict[str, str] | None = None) -> float:
        """Get gauge value."""
        return self.get_value(labels)

    def get_value(self, labels: dict[str, str] | None = None) -> float:
        """Get gauge value."""
        key = self._key(labels or self.labels)
        return self._values.get(key, 0.0)

    @property
    def value(self) -> float:
        """value ."""
        return self.get_value()

class Histogram(Metric):
    """Histogram metric for distributions."""

    DEFAULT_BUCKETS = [0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]

    def __init__(
        self,
        name: str,
        description: str = "",
        labels: dict[str, str] | list[str] | None = None,
        buckets: list[float] | None = None,
    ):
        allowed = labels
        if isinstance(labels, dict):
            allowed = list(labels.keys())
        super().__init__(name, description, allowed)
        self.buckets = sorted(buckets or self.DEFAULT_BUCKETS)
        self.labels = labels if isinstance(labels, dict) else {}
        self.values: list[float] = []
        self._bucket_counts: dict[float, int] = dict.fromkeys(self.buckets, 0)

    @property
    def metric_type(self) -> MetricType:
        return MetricType.HISTOGRAM

    def observe(self, value: float) -> None:
        """Observe a value."""
        with self._lock:
            self.values.append(value)
            for bucket in self.buckets:
                if value <= bucket:
                    self._bucket_counts[bucket] += 1

    def get(self, labels: dict[str, str] | None = None) -> dict[str, Any]:
        """Get histogram stats."""
        return self.get_value(labels)

    def get_value(self, labels: dict[str, str] | None = None) -> dict[str, Any]:
        """Get histogram stats."""
        with self._lock:
            if not self.values:
                return {"count": 0, "sum": 0.0, "min": 0.0, "max": 0.0, "avg": 0.0, "buckets": self._bucket_counts}

            return {
                "count": len(self.values),
                "sum": sum(self.values),
                "min": min(self.values),
                "max": max(self.values),
                "avg": sum(self.values) / len(self.values),
                "mean": sum(self.values) / len(self.values),
                "buckets": dict(self._bucket_counts),
            }

class Summary(Metric):
    """Summary metric with quantiles."""

    DEFAULT_QUANTILES = [0.5, 0.9, 0.95, 0.99]

    def __init__(
        self,
        name: str,
        description: str = "",
        labels: dict[str, str] | list[str] | None = None,
        quantiles: list[float] | None = None,
    ):
        allowed = labels
        if isinstance(labels, dict):
            allowed = list(labels.keys())
        super().__init__(name, description, allowed)
        self.quantiles = quantiles or self.DEFAULT_QUANTILES
        self.labels = labels if isinstance(labels, dict) else {}
        self.count: int = 0
        self.sum: float = 0.0
        self._observations: list[float] = []

    @property
    def metric_type(self) -> MetricType:
        return MetricType.SUMMARY

    def observe(self, value: float) -> None:
        """Observe a value."""
        with self._lock:
            self.count += 1
            self.sum += value
            self._observations.append(value)

    def get(self, labels: dict[str, str] | None = None) -> dict[str, Any]:
        """Get summary stats."""
        return self.get_value(labels)

    def get_value(self, labels: dict[str, str] | None = None) -> dict[str, Any]:
        """Get summary stats with quantiles."""
        with self._lock:
            if self.count == 0:
                return {"count": 0, "sum": 0.0, "avg": 0.0, "quantiles": {}}

            sorted_obs = sorted(self._observations)
            quantile_values = {}

            for q in self.quantiles:
                idx = int(len(sorted_obs) * q)
                idx = min(idx, len(sorted_obs) - 1)
                quantile_values[q] = sorted_obs[idx]

            return {
                "count": self.count,
                "sum": self.sum,
                "avg": self.sum / self.count,
                "quantiles": quantile_values,
            }


class Timer:
    """Context manager for timing operations."""

    def __init__(self, histogram: Histogram):
        self.histogram = histogram
        self._start: float = 0

    def __enter__(self):
        """enter ."""
        self._start = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """exit ."""
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
        with self._lock:
            return self._metrics.get(name)
from .aggregator import MetricAggregator

try:
    from .prometheus_exporter import PrometheusExporter
except ImportError:
    PrometheusExporter = None

try:
    from .statsd_client import StatsDClient
except ImportError:
    StatsDClient = None


try:
    from codomyrmex.exceptions import CodomyrmexError
except ImportError:
    class CodomyrmexError(Exception): pass

class MetricsError(CodomyrmexError):
    """Base class for metrics errors."""
    pass

# Alias for compatibility with older tests/code
class Metrics(MetricsRegistry):
    """Alias for MetricsRegistry for compatibility."""
    def __init__(self, backend="in_memory"):
        super().__init__()
        self.backend = backend
        self._counters: dict[str, Counter] = {}
        self._gauges: dict[str, Gauge] = {}
        self._histograms: dict[str, Histogram] = {}
        self._summaries: dict[str, Summary] = {}

    def _make_key(self, name: str, labels: dict | None = None) -> str:
        """Create a key from name and labels."""
        if labels:
            label_str = ",".join(f"{k}={v}" for k, v in sorted(labels.items()))
            return f"{name}{{{label_str}}}"
        return name

    def counter(self, name: str, labels: dict | None = None, description: str = "") -> Counter:
        """counter ."""
        key = self._make_key(name, labels)
        if key not in self._counters:
            self._counters[key] = Counter(name=name, labels=labels, description=description)
        return self._counters[key]

    def gauge(self, name: str, labels: dict | None = None, description: str = "") -> Gauge:
        """gauge ."""
        key = self._make_key(name, labels)
        if key not in self._gauges:
            self._gauges[key] = Gauge(name=name, labels=labels, description=description)
        return self._gauges[key]

    def histogram(self, name: str, labels: dict | None = None, description: str = "") -> Histogram:
        """histogram ."""
        key = self._make_key(name, labels)
        if key not in self._histograms:
            self._histograms[key] = Histogram(name=name, labels=labels, description=description)
        return self._histograms[key]

    def summary(self, name: str, labels: dict | None = None, description: str = "") -> Summary:
        """summary ."""
        key = self._make_key(name, labels)
        if key not in self._summaries:
            self._summaries[key] = Summary(name=name, labels=labels, description=description)
        return self._summaries[key]

    def export(self) -> dict[str, Any]:
        """Export all metrics to a dictionary."""
        return {
            "counters": {k: {"value": c.value, "labels": c.labels} for k, c in self._counters.items()},
            "gauges": {k: {"value": g.value, "labels": g.labels} for k, g in self._gauges.items()},
            "histograms": {k: {"stats": h.get(), "labels": h.labels} for k, h in self._histograms.items()},
            "summaries": {k: {"stats": s.get(), "labels": s.labels} for k, s in self._summaries.items()},
        }

    def export_prometheus(self) -> str:
        """Export metrics in Prometheus format."""
        lines = []
        for key, counter in self._counters.items():
            val = counter.value
            if "{" in key:
                name = key.split("{")[0]
                labels = key.split("{")[1].rstrip("}")
                labels = labels.replace("=", '="').replace(",", '",') + '"'
                lines.append(f"{name}_total{{{labels}}} {val}")
            else:
                lines.append(f"{counter.name}_total {val}")

        for key, gauge in self._gauges.items():
            val = gauge.value
            if "{" in key:
                name = key.split("{")[0]
                labels = key.split("{")[1].rstrip("}")
                labels = labels.replace("=", '="').replace(",", '",') + '"'
                lines.append(f"{name}{{{labels}}} {val}")
            else:
                lines.append(f"{gauge.name} {val}")

        for key, histogram in self._histograms.items():
            stats = histogram.get()
            if "{" in key:
                name = key.split("{")[0]
                labels = key.split("{")[1].rstrip("}")
                labels = labels.replace("=", '="').replace(",", '",') + '"'
                lines.append(f"{name}_count{{{labels}}} {stats['count']}")
                lines.append(f"{name}_sum{{{labels}}} {stats['sum']}")
            else:
                lines.append(f"{histogram.name}_count {stats['count']}")
                lines.append(f"{histogram.name}_sum {stats['sum']}")

        return "\n".join(lines)

def get_metrics(backend="in_memory") -> Metrics:
    """Helper to get a metrics instance."""
    return Metrics(backend=backend)


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
    "Metrics",
    "MetricsError",
    "get_metrics",
    "MetricAggregator",
    "PrometheusExporter",
    "StatsDClient",
]
