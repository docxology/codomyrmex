"""Optional dependency shims for data_visualization engines.

Single point of truth for the performance monitoring guarded import
so the fallback stubs are not duplicated across advanced_plotter.py and plotter.py.
"""

try:
    from codomyrmex.performance import monitor_performance, performance_context
    PERFORMANCE_MONITORING_AVAILABLE = True
except ImportError:
    PERFORMANCE_MONITORING_AVAILABLE = False

    def monitor_performance(*args, **kwargs):
        """No-op when codomyrmex.performance is not installed."""
        def decorator(func):
            return func
        return decorator

    class performance_context:
        """No-op context manager when codomyrmex.performance is not installed."""
        def __init__(self, *args, **kwargs):
            pass
        def __enter__(self):
            return self
        def __exit__(self, *args):
            pass


__all__ = ["monitor_performance", "performance_context", "PERFORMANCE_MONITORING_AVAILABLE"]
