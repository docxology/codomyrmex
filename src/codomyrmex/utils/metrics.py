"""
Observability Integration

Metrics collection and monitoring for all modules.
"""

import threading
import time
from collections.abc import Callable
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class MetricType(Enum):
    """Types of metrics."""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"


@dataclass
class MetricValue:
    """A single metric value."""
    name: str
    value: float
    timestamp: datetime = field(default_factory=datetime.now)
    labels: dict[str, str] = field(default_factory=dict)
    metric_type: MetricType = MetricType.GAUGE


class MetricsCollector:
    """Collect and aggregate metrics from modules."""

    _instance = None

    def __new__(cls):
        """New."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._metrics: dict[str, list[MetricValue]] = {}
            cls._instance._counters: dict[str, float] = {}
            cls._instance._gauges: dict[str, float] = {}
            cls._instance._histograms: dict[str, list[float]] = {}
            cls._instance._lock = threading.Lock()
        return cls._instance

    def increment(
        self,
        name: str,
        value: float = 1.0,
        labels: dict[str, str] | None = None,
    ) -> None:
        """Increment a counter."""
        key = self._make_key(name, labels)
        with self._lock:
            self._counters[key] = self._counters.get(key, 0) + value

    def set_gauge(
        self,
        name: str,
        value: float,
        labels: dict[str, str] | None = None,
    ) -> None:
        """Set a gauge value."""
        key = self._make_key(name, labels)
        with self._lock:
            self._gauges[key] = value

    def observe(
        self,
        name: str,
        value: float,
        labels: dict[str, str] | None = None,
    ) -> None:
        """Add observation to histogram."""
        key = self._make_key(name, labels)
        with self._lock:
            if key not in self._histograms:
                self._histograms[key] = []
            self._histograms[key].append(value)

    def _make_key(self, name: str, labels: dict[str, str] | None) -> str:
        """Create unique key from name and labels."""
        if not labels:
            return name
        label_str = ",".join(f"{k}={v}" for k, v in sorted(labels.items()))
        return f"{name}{{{label_str}}}"

    def get_all(self) -> dict[str, Any]:
        """Get all metrics."""
        with self._lock:
            result = {
                "counters": dict(self._counters),
                "gauges": dict(self._gauges),
                "histograms": {},
            }

            for key, values in self._histograms.items():
                if values:
                    result["histograms"][key] = {
                        "count": len(values),
                        "sum": sum(values),
                        "min": min(values),
                        "max": max(values),
                        "avg": sum(values) / len(values),
                    }

            return result

    def reset(self) -> None:
        """Reset all metrics."""
        with self._lock:
            self._counters.clear()
            self._gauges.clear()
            self._histograms.clear()


# Global collector instance
metrics = MetricsCollector()


@contextmanager
def timed_metric(name: str, labels: dict[str, str] | None = None):
    """Context manager to time operations and record as histogram."""
    start = time.time()
    try:
        yield
    finally:
        elapsed = (time.time() - start) * 1000  # In milliseconds
        metrics.observe(f"{name}_duration_ms", elapsed, labels)


def count_calls(name: str, labels: dict[str, str] | None = None):
    """Decorator to count function calls."""
    def decorator(func: Callable) -> Callable:
        """Decorator."""
        import functools

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            """Wrapper."""
            metrics.increment(f"{name}_calls_total", labels=labels)
            try:
                result = func(*args, **kwargs)
                metrics.increment(f"{name}_success_total", labels=labels)
                return result
            except Exception:
                metrics.increment(f"{name}_errors_total", labels=labels)
                raise

        return wrapper
    return decorator


class ModuleHealth:
    """Track health of modules."""

    def __init__(self):
        self._health: dict[str, bool] = {}
        self._last_check: dict[str, datetime] = {}
        self._check_fns: dict[str, Callable[[], bool]] = {}

    def register(self, module: str, check_fn: Callable[[], bool]) -> None:
        """Register a health check function."""
        self._check_fns[module] = check_fn

    def check(self, module: str) -> bool:
        """Check health of a module."""
        if module in self._check_fns:
            try:
                self._health[module] = self._check_fns[module]()
            except Exception:
                self._health[module] = False
            self._last_check[module] = datetime.now()
        return self._health.get(module, False)

    def check_all(self) -> dict[str, bool]:
        """Check all registered modules."""
        return {module: self.check(module) for module in self._check_fns}

    def is_healthy(self) -> bool:
        """Check if all modules are healthy."""
        return all(self.check_all().values())


health = ModuleHealth()


# Prometheus-compatible export
def export_prometheus() -> str:
    """Export metrics in Prometheus format."""
    lines = []
    data = metrics.get_all()

    for name, value in data["counters"].items():
        lines.append(f"# TYPE {name.split('{')[0]} counter")
        lines.append(f"{name} {value}")

    for name, value in data["gauges"].items():
        lines.append(f"# TYPE {name.split('{')[0]} gauge")
        lines.append(f"{name} {value}")

    for name, hist in data["histograms"].items():
        base = name.split('{')[0]
        lines.append(f"# TYPE {base} histogram")
        lines.append(f"{name}_sum {hist['sum']}")
        lines.append(f"{name}_count {hist['count']}")

    return "\n".join(lines)


__all__ = [
    "MetricType",
    "MetricValue",
    "MetricsCollector",
    "metrics",
    "timed_metric",
    "count_calls",
    "ModuleHealth",
    "health",
    "export_prometheus",
]
