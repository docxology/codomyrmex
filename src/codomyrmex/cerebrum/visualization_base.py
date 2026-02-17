"""Re-export shim for backward compatibility.

The visualization_base module was moved to cerebrum/visualization/visualization_base.py.
This shim re-exports all symbols for modules that import from the old path:
    from codomyrmex.cerebrum.visualization_base import BaseNetworkVisualizer
"""

from .visualization.visualization_base import (  # noqa: F401
    BaseChartVisualizer,
    BaseNetworkVisualizer,
)
