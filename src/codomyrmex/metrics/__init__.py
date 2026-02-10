"""
Metrics module for Codomyrmex.

This module provides metrics collection, aggregation, and Prometheus integration.
"""

from codomyrmex.exceptions import CodomyrmexError

# Shared schemas for cross-module interop
try:
    from codomyrmex.schemas import Result, ResultStatus
except ImportError:
    Result = None
    ResultStatus = None

from .aggregator import MetricAggregator
from .metrics import Counter, Gauge, Histogram, Metrics, Summary

# Optional dependencies
try:
    from .prometheus_exporter import PrometheusExporter
except ImportError:
    PrometheusExporter = None  # prometheus_client not installed

try:
    from .statsd_client import StatsDClient
except ImportError:
    StatsDClient = None  # statsd not installed

def cli_commands():
    """Return CLI commands for the metrics module."""
    def _collectors(**kwargs):
        """List metric collectors."""
        print("=== Metric Collectors ===")
        print("  Counter    - Monotonically increasing counter")
        print("  Gauge      - Value that can go up and down")
        print("  Histogram  - Distribution of values")
        print("  Summary    - Quantile summaries")
        print("\nExporters:")
        print(f"  Prometheus: {'available' if PrometheusExporter is not None else 'not installed'}")
        print(f"  StatsD:     {'available' if StatsDClient is not None else 'not installed'}")
        print(f"  Aggregator: MetricAggregator (always available)")

    def _report(**kwargs):
        """Show metrics report."""
        print("=== Metrics Report ===")
        try:
            m = get_metrics()
            stats = m.get_all() if hasattr(m, "get_all") else {}
            if stats:
                for name, value in stats.items():
                    print(f"  {name}: {value}")
            else:
                print("  No metrics recorded yet")
        except Exception as e:
            print(f"  Could not retrieve metrics: {e}")

    return {
        "collectors": {"handler": _collectors, "help": "List metric collectors"},
        "report": {"handler": _report, "help": "Show metrics report"},
    }


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
    "cli_commands",
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


