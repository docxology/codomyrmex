"""
Metrics module for Codomyrmex.

This module provides metrics collection, aggregation, and Prometheus integration.
"""

from codomyrmex.exceptions import CodomyrmexError

from .metrics import Counter, Gauge, Histogram, Metrics, Summary
from .prometheus_exporter import PrometheusExporter
from .statsd_client import StatsDClient
from .aggregator import MetricAggregator

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


