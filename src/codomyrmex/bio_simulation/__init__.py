"""Bio-Simulation Module for Codomyrmex.

Provides ant colony simulation and genomics integration.
"""

# Lazy imports
try:
    from .ant_colony import Colony
except ImportError:
    Colony = None

__all__ = ["Colony"]
