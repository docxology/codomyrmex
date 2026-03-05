"""Compatibility shims for optional codomyrmex.coding.review dependencies."""

from __future__ import annotations

from contextlib import nullcontext

try:
    from codomyrmex.performance import monitor_performance, performance_context
except ImportError:
    performance_context = nullcontext

    def monitor_performance(*args, **kwargs):
        """No-op decorator used when codomyrmex.performance is not installed."""
        def decorator(func):
            return func
        return decorator


__all__ = ["monitor_performance", "performance_context"]
