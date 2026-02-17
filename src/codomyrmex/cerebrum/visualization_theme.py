"""Re-export shim for backward compatibility.

The visualization_theme module was moved to cerebrum/visualization/visualization_theme.py.
This shim re-exports all symbols for modules that import from the old path.
"""

from .visualization.visualization_theme import *  # noqa: F401, F403

# Provide explicit re-exports for known consumers
try:
    from .visualization.visualization_theme import get_default_theme  # noqa: F401
except ImportError:
    pass
