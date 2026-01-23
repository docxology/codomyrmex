"""
Metrics module for Codomyrmex.

This module provides metrics collection, aggregation, and Prometheus integration.
"""

from codomyrmex.exceptions import CodomyrmexError

from .metrics import Counter, Gauge, Histogram, Metrics, Summary
from .aggregator import MetricAggregator

# Optional dependencies
try:
    from .prometheus_exporter import PrometheusExporter
except ImportError:
    PrometheusExporter = None  # prometheus_client not installed

try:
    from .statsd_client import StatsDClient
except ImportError:
    StatsDClient = None  # statsd not installed

__all__ = [
    "Metrics",
    "Counter",
    "Gauge",
    "Histogram",
    "Summary",
    "PrometheusExporter",
    "StatsDClient",
    "MetricAggregator",
    "get_metrics",
]

__version__ = "0.1.0"


class MetricsError(CodomyrmexError):
    """Raised when metrics operations fail."""

    pass


def get_metrics(backend: str = "in_memory") -> Metrics:
    """Get a metrics instance.

    Args:
        backend: Metrics backend (in_memory, prometheus)

    Returns:
        Metrics instance
    """
    return Metrics(backend=backend)


