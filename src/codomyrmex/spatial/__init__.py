"""
Spatial modeling module for Codomyrmex.
Provides submodules for 3D modeling, 4D modeling (Synergetics), and world models.
"""

from . import three_d
from . import four_d
from . import world_models

# New submodules
from . import coordinates
from . import rendering
from . import physics

__all__ = [
    "three_d",
    "four_d",
    "world_models",
    "coordinates",
    "rendering",
    "physics",
]

