"""Optional performance instrumentation for code review operations."""

from __future__ import annotations

from contextlib import nullcontext

try:
    from codomyrmex.performance import monitor_performance, performance_context
except ImportError:
    performance_context = nullcontext  # type: ignore

    def monitor_performance(*args, **kwargs):
        """Return a transparent decorator when performance support is absent."""

        def decorator(func):
            return func

        return decorator


__all__ = ["monitor_performance", "performance_context"]
