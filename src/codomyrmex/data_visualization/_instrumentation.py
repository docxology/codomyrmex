"""Optional performance instrumentation for visualization engines.

The performance monitor is optional, but plotting engines should retain one
stable instrumentation interface whether or not that extra is installed.
"""

import warnings

try:
    from codomyrmex.performance import monitor_performance, performance_context

    PERFORMANCE_MONITORING_AVAILABLE = True
except ImportError:
    PERFORMANCE_MONITORING_AVAILABLE = False
    warnings.warn(
        "codomyrmex.performance is not installed; performance monitoring is disabled "
        "for data_visualization. Install with: uv sync --extra performance",
        ImportWarning,
        stacklevel=2,
    )

    def monitor_performance(*args, **kwargs):
        """Return a transparent decorator when performance support is absent."""

        def decorator(func):
            return func

        return decorator

    class performance_context:
        """Transparent context manager when performance support is absent."""

        def __init__(self, *args, **kwargs):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass


__all__ = [
    "PERFORMANCE_MONITORING_AVAILABLE",
    "monitor_performance",
    "performance_context",
]
