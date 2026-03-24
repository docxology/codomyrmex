"""
Engines submodule for data_visualization.

Provides core plotting engines and utilities.
"""

from codomyrmex.data_visualization.utils import (
    apply_style,
    save_plot,
)

from .plotter import Plotter

try:
    from .advanced_plotter import AdvancedPlotter

    _HAS_ADVANCED = True
except ImportError:  # matplotlib / numpy / seaborn not installed
    _HAS_ADVANCED = False

__all__ = [
    "Plotter",
    "apply_style",
    "save_plot",
]

if _HAS_ADVANCED:
    __all__.append("AdvancedPlotter")

