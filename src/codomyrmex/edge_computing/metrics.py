# DEPRECATED(v0.2.0): Shim module. Import from edge_computing.infrastructure.metrics instead. Will be removed in v0.3.0.
"""Backward-compatibility shim for edge_computing.metrics.

The metrics module has moved to edge_computing.infrastructure.metrics.
This shim re-exports its public symbols so that existing imports
like ``from codomyrmex.edge_computing.metrics import EdgeMetrics``
continue to work.
"""

from .infrastructure.metrics import EdgeMetrics, InvocationRecord

__all__ = ["EdgeMetrics", "InvocationRecord"]
