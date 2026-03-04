"""Tests for spatial MCP tools."""

from __future__ import annotations

import math


class TestSpatialCartesianToSpherical:
    """Tests for spatial_cartesian_to_spherical MCP tool."""

    def test_origin(self):
        from codomyrmex.spatial.mcp_tools import spatial_cartesian_to_spherical

        result = spatial_cartesian_to_spherical(x=0.0, y=0.0, z=0.0)
        assert result["status"] == "success"
        assert result["r"] == 0.0

    def test_unit_z(self):
        from codomyrmex.spatial.mcp_tools import spatial_cartesian_to_spherical

        result = spatial_cartesian_to_spherical(x=0.0, y=0.0, z=1.0)
        assert result["status"] == "success"
        assert abs(result["r"] - 1.0) < 1e-9
        assert abs(result["phi"]) < 1e-9  # phi=0 for z-axis

    def test_known_point(self):
        from codomyrmex.spatial.mcp_tools import spatial_cartesian_to_spherical

        result = spatial_cartesian_to_spherical(x=1.0, y=1.0, z=1.0)
        assert result["status"] == "success"
        assert abs(result["r"] - math.sqrt(3)) < 1e-9


class TestSpatialGeographicDistance:
    """Tests for spatial_geographic_distance MCP tool."""

    def test_same_point(self):
        from codomyrmex.spatial.mcp_tools import spatial_geographic_distance

        result = spatial_geographic_distance(lat1=40.0, lon1=-74.0, lat2=40.0, lon2=-74.0)
        assert result["status"] == "success"
        assert result["distance_meters"] < 1.0

    def test_known_distance(self):
        """Test distance between New York and London (approx 5570 km)."""
        from codomyrmex.spatial.mcp_tools import spatial_geographic_distance

        result = spatial_geographic_distance(
            lat1=40.7128, lon1=-74.0060,  # NYC
            lat2=51.5074, lon2=-0.1278,   # London
        )
        assert result["status"] == "success"
        assert 5500 < result["distance_km"] < 5700

    def test_bearing_returned(self):
        from codomyrmex.spatial.mcp_tools import spatial_geographic_distance

        result = spatial_geographic_distance(lat1=0.0, lon1=0.0, lat2=0.0, lon2=90.0)
        assert result["status"] == "success"
        assert "bearing_degrees" in result
        assert abs(result["bearing_degrees"] - 90.0) < 1.0


class TestSpatialPointDistance:
    """Tests for spatial_point_distance MCP tool."""

    def test_same_point(self):
        from codomyrmex.spatial.mcp_tools import spatial_point_distance

        result = spatial_point_distance(x1=1, y1=2, z1=3, x2=1, y2=2, z2=3)
        assert result["status"] == "success"
        assert result["distance"] == 0.0

    def test_known_distance(self):
        from codomyrmex.spatial.mcp_tools import spatial_point_distance

        result = spatial_point_distance(x1=0, y1=0, z1=0, x2=3, y2=4, z2=0)
        assert result["status"] == "success"
        assert abs(result["distance"] - 5.0) < 1e-9

    def test_midpoint(self):
        from codomyrmex.spatial.mcp_tools import spatial_point_distance

        result = spatial_point_distance(x1=0, y1=0, z1=0, x2=10, y2=10, z2=10)
        assert result["status"] == "success"
        mid = result["midpoint"]
        assert abs(mid["x"] - 5.0) < 1e-9
        assert abs(mid["y"] - 5.0) < 1e-9
        assert abs(mid["z"] - 5.0) < 1e-9
