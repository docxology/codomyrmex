"""MCP tool definitions for the spatial module.

Exposes coordinate transformations and distance calculations as MCP tools.
"""

from __future__ import annotations

from typing import Any

from codomyrmex.model_context_protocol.decorators import mcp_tool


def _get_coordinates():
    """Lazy import of coordinate classes."""
    from codomyrmex.spatial.coordinates import (
        GeographicCoord,
        Point3D,
        SphericalCoord,
    )

    return Point3D, SphericalCoord, GeographicCoord


@mcp_tool(
    category="spatial",
    description="Transform 3D Cartesian coordinates to spherical coordinates.",
)
def spatial_cartesian_to_spherical(
    x: float,
    y: float,
    z: float,
) -> dict[str, Any]:
    """Convert Cartesian (x, y, z) to spherical (r, theta, phi) coordinates.

    Args:
        x: X coordinate.
        y: Y coordinate.
        z: Z coordinate.

    Returns:
        dict with keys: status, r, theta, phi
    """
    try:
        Point3D, SphericalCoord, _ = _get_coordinates()
        point = Point3D(x, y, z)
        spherical = SphericalCoord.from_cartesian(point)
        return {
            "status": "success",
            "r": spherical.r,
            "theta": spherical.theta,
            "phi": spherical.phi,
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    category="spatial",
    description="Calculate great-circle distance between two geographic coordinates in meters.",
)
def spatial_geographic_distance(
    lat1: float,
    lon1: float,
    lat2: float,
    lon2: float,
) -> dict[str, Any]:
    """Calculate great-circle distance between two geographic points.

    Uses the Haversine formula for accuracy on the Earth's surface.

    Args:
        lat1: Latitude of first point (degrees).
        lon1: Longitude of first point (degrees).
        lat2: Latitude of second point (degrees).
        lon2: Longitude of second point (degrees).

    Returns:
        dict with keys: status, distance_meters, distance_km, bearing_degrees
    """
    try:
        _, _, GeographicCoord = _get_coordinates()
        coord1 = GeographicCoord(lat=lat1, lon=lon1)
        coord2 = GeographicCoord(lat=lat2, lon=lon2)
        distance = coord1.distance_to(coord2)
        bearing = coord1.bearing_to(coord2)
        return {
            "status": "success",
            "distance_meters": distance,
            "distance_km": distance / 1000.0,
            "bearing_degrees": bearing,
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    category="spatial",
    description="Calculate Euclidean distance and vector operations between two 3D points.",
)
def spatial_point_distance(
    x1: float,
    y1: float,
    z1: float,
    x2: float,
    y2: float,
    z2: float,
) -> dict[str, Any]:
    """Calculate distance and midpoint between two 3D points.

    Args:
        x1: X coordinate of first point.
        y1: Y coordinate of first point.
        z1: Z coordinate of first point.
        x2: X coordinate of second point.
        y2: Y coordinate of second point.
        z2: Z coordinate of second point.

    Returns:
        dict with keys: status, distance, midpoint, dot_product
    """
    try:
        Point3D, _, _ = _get_coordinates()
        p1 = Point3D(x1, y1, z1)
        p2 = Point3D(x2, y2, z2)
        midpoint = (p1 + p2) / 2.0
        return {
            "status": "success",
            "distance": p1.distance_to(p2),
            "midpoint": {"x": midpoint.x, "y": midpoint.y, "z": midpoint.z},
            "dot_product": p1.dot(p2),
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}
