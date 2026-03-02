"""
Metric Collector

Collects and stores time-series metrics.
"""

import threading
from datetime import datetime, timedelta

from .models import MetricType, MetricValue


class MetricCollector:
    """
    Collects and stores metrics.

    Usage:
        collector = MetricCollector()

        collector.record("http_requests_total", 1, labels={"method": "GET"})
        collector.record("cpu_usage", 0.75)

        metrics = collector.get_metrics("http_requests_total")
    """

    def __init__(self, retention_minutes: int = 60):
        """Initialize this instance."""
        self.retention_minutes = retention_minutes
        self._metrics: dict[str, list[MetricValue]] = {}
        self._lock = threading.Lock()

    def record(
        self,
        name: str,
        value: float,
        labels: dict[str, str] | None = None,
        metric_type: MetricType = MetricType.GAUGE,
    ) -> None:
        """Record a metric value."""
        metric = MetricValue(
            name=name,
            value=value,
            labels=labels or {},
            metric_type=metric_type,
        )

        with self._lock:
            if name not in self._metrics:
                self._metrics[name] = []
            self._metrics[name].append(metric)

    def get_metrics(
        self,
        name: str,
        start: datetime | None = None,
        end: datetime | None = None,
    ) -> list[MetricValue]:
        """Get metrics by name."""
        if name not in self._metrics:
            return []

        metrics = self._metrics[name]

        if start:
            metrics = [m for m in metrics if m.timestamp >= start]
        if end:
            metrics = [m for m in metrics if m.timestamp <= end]

        return metrics

    def get_latest(self, name: str) -> MetricValue | None:
        """Get latest metric value."""
        metrics = self._metrics.get(name, [])
        return metrics[-1] if metrics else None

    def list_metric_names(self) -> list[str]:
        """List all metric names."""
        return list(self._metrics.keys())

    def cleanup_old(self) -> int:
        """Remove old metrics beyond retention."""
        cutoff = datetime.now() - timedelta(minutes=self.retention_minutes)
        removed = 0

        with self._lock:
            for name in self._metrics:
                before = len(self._metrics[name])
                self._metrics[name] = [m for m in self._metrics[name] if m.timestamp > cutoff]
                removed += before - len(self._metrics[name])

        return removed
