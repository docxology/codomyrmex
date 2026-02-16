"""Backward-compatibility shim for edge_computing.metrics.

The metrics module has moved to edge_computing.infrastructure.metrics.
This shim re-exports its public symbols so that existing imports
like ``from codomyrmex.edge_computing.metrics import EdgeMetrics``
continue to work.
"""

from .infrastructure.metrics import EdgeMetrics, InvocationRecord

__all__ = ["EdgeMetrics", "InvocationRecord"]
