from typing import Any, Optional

from dataclasses import dataclass, field

from codomyrmex.logging_monitoring.logger_config import get_logger




























"""
Metrics collection and aggregation.
"""



logger = get_logger(__name__)


@dataclass
class Counter:
    """Counter metric."""

    name: str
    labels: dict[str, str] = field(default_factory=dict)
    value: float = 0.0

    def inc(self, value: float = 1.0) -> None:
        """Increment counter."""
        self.value += value

    def get(self) -> float:
        """Get counter value."""
        return self.value


@dataclass
class Gauge:
    """Gauge metric."""

    name: str
    labels: dict[str, str] = field(default_factory=dict)
    value: float = 0.0

    def set(self, value: float) -> None:
        """Set gauge value."""
        self.value = value

    def inc(self, value: float = 1.0) -> None:
        """Increment gauge."""
        self.value += value

    def dec(self, value: float = 1.0) -> None:
        """Decrement gauge."""
        self.value -= value

    def get(self) -> float:
        """Get gauge value."""
        return self.value


@dataclass
class Histogram:
    """Histogram metric."""

    name: str
    labels: dict[str, str] = field(default_factory=dict)
    values: list[float] = field(default_factory=list)

    def observe(self, value: float) -> None:
        """Record a value."""
        self.values.append(value)

    def get(self) -> dict[str, Any]:
        """Get histogram statistics."""
        if not self.values:
            return {"count": 0, "sum": 0.0, "min": 0.0, "max": 0.0, "avg": 0.0}

        return {
            "count": len(self.values),
            "sum": sum(self.values),
            "min": min(self.values),
            "max": max(self.values),
            "avg": sum(self.values) / len(self.values),
        }


@dataclass
class Summary:
    """Summary metric."""

    name: str
    labels: dict[str, str] = field(default_factory=dict)
    count: int = 0
    sum: float = 0.0

    def observe(self, value: float) -> None:
        """Record a value."""
        self.count += 1
        self.sum += value

    def get(self) -> dict[str, Any]:
        """Get summary statistics."""
        return {
            "count": self.count,
            "sum": self.sum,
            "avg": self.sum / self.count if self.count > 0 else 0.0,
        }


class Metrics:
    """Metrics collection and aggregation."""

    def __init__(self, backend: str = "in_memory"):
        """Initialize metrics.

        Args:
            backend: Metrics backend (in_memory, prometheus)
        """
        self.backend = backend
        self._counters: dict[str, Counter] = {}
        self._gauges: dict[str, Gauge] = {}
        self._histograms: dict[str, Histogram] = {}
        self._summaries: dict[str, Summary] = {}

    def _make_key(self, name: str, labels: Optional[dict] = None) -> str:
        """Create a key from name and labels."""
        if labels:
            label_str = ",".join(f"{k}={v}" for k, v in sorted(labels.items()))
            return f"{name}{{{label_str}}}"
        return name

    def counter(self, name: str, labels: Optional[dict] = None) -> Counter:
        """Create or get a counter metric.

        Args:
            name: Metric name
            labels: Optional labels

        Returns:
            Counter metric
        """
        key = self._make_key(name, labels)
        if key not in self._counters:
            self._counters[key] = Counter(name=name, labels=labels or {})
        return self._counters[key]

    def gauge(self, name: str, labels: Optional[dict] = None) -> Gauge:
        """Create or get a gauge metric.

        Args:
            name: Metric name
            labels: Optional labels

        Returns:
            Gauge metric
        """
        key = self._make_key(name, labels)
        if key not in self._gauges:
            self._gauges[key] = Gauge(name=name, labels=labels or {})
        return self._gauges[key]

    def histogram(self, name: str, labels: Optional[dict] = None) -> Histogram:
        """Create or get a histogram metric.

        Args:
            name: Metric name
            labels: Optional labels

        Returns:
            Histogram metric
        """
        key = self._make_key(name, labels)
        if key not in self._histograms:
            self._histograms[key] = Histogram(name=name, labels=labels or {})
        return self._histograms[key]

    def summary(self, name: str, labels: Optional[dict] = None) -> Summary:
        """Create or get a summary metric.

        Args:
            name: Metric name
            labels: Optional labels

        Returns:
            Summary metric
        """
        key = self._make_key(name, labels)
        if key not in self._summaries:
            self._summaries[key] = Summary(name=name, labels=labels or {})
        return self._summaries[key]

    def export(self) -> dict[str, Any]:
        """Export all metrics to a dictionary.

        Returns:
            Dictionary containing all metrics
        """
        return {
            "counters": {k: {"value": c.value, "labels": c.labels} for k, c in self._counters.items()},
            "gauges": {k: {"value": g.value, "labels": g.labels} for k, g in self._gauges.items()},
            "histograms": {k: {"stats": h.get(), "labels": h.labels} for k, h in self._histograms.items()},
            "summaries": {k: {"stats": s.get(), "labels": s.labels} for k, s in self._summaries.items()},
        }

    def export_prometheus(self) -> str:
        """Export metrics in Prometheus format.

        Returns:
            Prometheus-formatted metrics string
        """
        lines = []
        for counter in self._counters.values():
            label_str = ",".join(f'{k}="{v}"' for k, v in counter.labels.items()) if counter.labels else ""
            metric_name = f"{counter.name}_total"
            if label_str:
                lines.append(f"{metric_name}{{{label_str}}} {counter.value}")
            else:
                lines.append(f"{metric_name} {counter.value}")

        for gauge in self._gauges.values():
            label_str = ",".join(f'{k}="{v}"' for k, v in gauge.labels.items()) if gauge.labels else ""
            if label_str:
                lines.append(f"{gauge.name}{{{label_str}}} {gauge.value}")
            else:
                lines.append(f"{gauge.name} {gauge.value}")

        for histogram in self._histograms.values():
            stats = histogram.get()
            label_str = ",".join(f'{k}="{v}"' for k, v in histogram.labels.items()) if histogram.labels else ""
            if label_str:
                lines.append(f"{histogram.name}_count{{{label_str}}} {stats['count']}")
                lines.append(f"{histogram.name}_sum{{{label_str}}} {stats['sum']}")
            else:
                lines.append(f"{histogram.name}_count {stats['count']}")
                lines.append(f"{histogram.name}_sum {stats['sum']}")

        return "\n".join(lines)


