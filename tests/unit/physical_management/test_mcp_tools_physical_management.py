"""Tests for physical_management MCP tools.

Zero-mock tests that exercise the real physical_management MCP tool implementations.
"""

from __future__ import annotations


class TestPhysicalManagementListTypes:
    """Tests for physical_management_list_types MCP tool."""

    def test_returns_success_status(self):
        from codomyrmex.physical_management.mcp_tools import (
            physical_management_list_types,
        )

        result = physical_management_list_types()
        assert result["status"] == "success"

    def test_contains_object_types(self):
        from codomyrmex.physical_management.mcp_tools import (
            physical_management_list_types,
        )

        result = physical_management_list_types()
        assert "object_types" in result
        assert "sensor" in result["object_types"]
        assert "device" in result["object_types"]

    def test_contains_object_statuses(self):
        from codomyrmex.physical_management.mcp_tools import (
            physical_management_list_types,
        )

        result = physical_management_list_types()
        assert "object_statuses" in result
        assert "active" in result["object_statuses"]
        assert "inactive" in result["object_statuses"]

    def test_contains_material_types(self):
        from codomyrmex.physical_management.mcp_tools import (
            physical_management_list_types,
        )

        result = physical_management_list_types()
        assert "material_types" in result
        assert "metal" in result["material_types"]


class TestPhysicalManagementCreateObject:
    """Tests for physical_management_create_object MCP tool."""

    def test_creates_device(self):
        from codomyrmex.physical_management.mcp_tools import (
            physical_management_create_object,
        )

        result = physical_management_create_object(
            object_id="test-1",
            name="Test Device",
            object_type="device",
            x=1.0,
            y=2.0,
            z=3.0,
        )
        assert result["status"] == "success"
        obj = result["object"]
        assert obj["id"] == "test-1"
        assert obj["name"] == "Test Device"
        assert obj["object_type"] == "device"
        assert obj["location"] == (1.0, 2.0, 3.0)

    def test_creates_sensor_with_material(self):
        from codomyrmex.physical_management.mcp_tools import (
            physical_management_create_object,
        )

        result = physical_management_create_object(
            object_id="sensor-1",
            name="Temp Sensor",
            object_type="sensor",
            material="metal",
            mass=0.5,
        )
        assert result["status"] == "success"
        assert result["object"]["material"] == "metal"
        assert result["object"]["mass"] == 0.5

    def test_missing_id_returns_error(self):
        from codomyrmex.physical_management.mcp_tools import (
            physical_management_create_object,
        )

        result = physical_management_create_object(object_id="", name="no-id")
        assert result["status"] == "error"

    def test_invalid_type_returns_error(self):
        from codomyrmex.physical_management.mcp_tools import (
            physical_management_create_object,
        )

        result = physical_management_create_object(
            object_id="bad", name="bad", object_type="nonexistent"
        )
        assert result["status"] == "error"


class TestPhysicalManagementMaterialProperties:
    """Tests for physical_management_material_properties MCP tool."""

    def test_metal_properties(self):
        from codomyrmex.physical_management.mcp_tools import (
            physical_management_material_properties,
        )

        result = physical_management_material_properties(material="metal")
        assert result["status"] == "success"
        assert result["material"] == "metal"
        props = result["properties"]
        assert props["density"] == 7850
        assert props["friction_coefficient"] == 0.4

    def test_plastic_properties(self):
        from codomyrmex.physical_management.mcp_tools import (
            physical_management_material_properties,
        )

        result = physical_management_material_properties(material="plastic")
        assert result["status"] == "success"
        assert result["properties"]["density"] == 1200

    def test_invalid_material_returns_error(self):
        from codomyrmex.physical_management.mcp_tools import (
            physical_management_material_properties,
        )

        result = physical_management_material_properties(material="unobtanium")
        assert result["status"] == "error"
