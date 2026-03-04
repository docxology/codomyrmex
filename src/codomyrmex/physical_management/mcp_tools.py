"""MCP tool definitions for the physical_management module.

Exposes physical object creation, querying, and statistics as MCP tools.
"""

from __future__ import annotations

from typing import Any

from codomyrmex.model_context_protocol.decorators import mcp_tool


def _get_manager():
    """Lazy import of PhysicalObjectManager."""
    from codomyrmex.physical_management.object_manager import PhysicalObjectManager

    return PhysicalObjectManager()


@mcp_tool(
    category="physical_management",
    description="List available physical object types and status values.",
)
def physical_management_list_types() -> dict[str, Any]:
    """List all ObjectType and ObjectStatus enum values.

    Returns:
        dict with keys: status, object_types, object_statuses, material_types
    """
    try:
        from codomyrmex.physical_management.object_manager import (
            MaterialType,
            ObjectStatus,
            ObjectType,
        )

        return {
            "status": "success",
            "object_types": [t.value for t in ObjectType],
            "object_statuses": [s.value for s in ObjectStatus],
            "material_types": [m.value for m in MaterialType],
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    category="physical_management",
    description=(
        "Create a physical object and return its properties. "
        "Useful for registering sensors, devices, or structures."
    ),
)
def physical_management_create_object(
    object_id: str = "",
    name: str = "",
    object_type: str = "device",
    x: float = 0.0,
    y: float = 0.0,
    z: float = 0.0,
    material: str = "unknown",
    mass: float = 1.0,
) -> dict[str, Any]:
    """Create a physical object and return its serialized representation.

    Args:
        object_id: Unique identifier for the object.
        name: Human-readable name.
        object_type: One of sensor/actuator/device/container/vehicle/structure.
        x: X coordinate.
        y: Y coordinate.
        z: Z coordinate.
        material: Material type string.
        mass: Object mass in kg.

    Returns:
        dict with keys: status, object (serialized PhysicalObject)
    """
    if not object_id or not name:
        return {"status": "error", "message": "object_id and name are required"}
    try:
        from codomyrmex.physical_management.object_manager import (
            MaterialType,
            ObjectType,
            PhysicalObjectManager,
        )

        mgr = PhysicalObjectManager()
        obj_type = ObjectType(object_type)
        mat_type = MaterialType(material)
        obj = mgr.create_object(
            object_id=object_id,
            name=name,
            object_type=obj_type,
            x=x,
            y=y,
            z=z,
            material=mat_type,
            mass=mass,
        )
        return {"status": "success", "object": obj.to_dict()}
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    category="physical_management",
    description="Get material properties for a given material type (density, elasticity, etc.).",
)
def physical_management_material_properties(
    material: str = "metal",
) -> dict[str, Any]:
    """Look up physical material properties by material type name.

    Args:
        material: Material type (metal, plastic, wood, glass, ceramic, composite, liquid, gas, unknown).

    Returns:
        dict with keys: status, material, properties
    """
    try:
        from codomyrmex.physical_management.object_manager import (
            MaterialProperties,
            MaterialType,
        )

        mat_type = MaterialType(material)
        props = MaterialProperties.from_material_type(mat_type)
        return {
            "status": "success",
            "material": material,
            "properties": {
                "density": props.density,
                "elasticity": props.elasticity,
                "thermal_conductivity": props.thermal_conductivity,
                "specific_heat": props.specific_heat,
                "melting_point": props.melting_point,
                "friction_coefficient": props.friction_coefficient,
                "restitution": props.restitution,
            },
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}
