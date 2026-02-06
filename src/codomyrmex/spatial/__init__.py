"""
Spatial modeling module for Codomyrmex.
Provides submodules for 3D modeling, 4D modeling (Synergetics), and world models.
"""

# New submodules
from . import coordinates, four_d, physics, rendering, three_d, world_models

__all__ = [
    "three_d",
    "four_d",
    "world_models",
    "coordinates",
    "rendering",
    "physics",
]

