"""
Spatial modeling module for Codomyrmex.
Provides submodules for 3D modeling, 4D modeling (Synergetics), and world models.
"""

# Shared schemas for cross-module interop
import contextlib

with contextlib.suppress(ImportError):
    from codomyrmex.validation.schemas import Result, ResultStatus

# New submodules
from . import coordinates, four_d, physics, rendering, three_d, world_models


def cli_commands():
    """Return CLI commands for the spatial module."""

    def _list_coordinate_systems():
        """List coordinate systems."""
        print("Spatial Module - Coordinate Systems:")
        print("  cartesian   - 3D Cartesian (x, y, z)")
        print("  spherical   - Spherical (r, theta, phi)")
        print("  cylindrical - Cylindrical (r, theta, z)")
        print("  synergetics - 4D Synergetics (tetravolumes)")
        print("  geographic  - Geographic (lat, lon, alt)")

    def _spatial_status():
        """Show spatial engine status."""
        print("Spatial Module Status:")
        print("  three_d:      available")
        print("  four_d:       available (Synergetics)")
        print("  world_models: available")
        print("  coordinates:  available")
        print("  rendering:    available")
        print("  physics:      available")

    return {
        "coordinate_systems": _list_coordinate_systems,
        "status": _spatial_status,
    }


__all__ = [
    "cli_commands",
    "coordinates",
    "four_d",
    "physics",
    "rendering",
    "three_d",
    "world_models",
]
