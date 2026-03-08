# type: ignore
"""Data models for physical object management.

Enums, dataclasses, and spatial-index structures used by the
PhysicalObjectManager and ObjectRegistry.
"""

from __future__ import annotations

import math
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ObjectType(Enum):
    """Types of physical objects."""

    SENSOR = "sensor"
    ACTUATOR = "actuator"
    DEVICE = "device"
    CONTAINER = "container"
    VEHICLE = "vehicle"
    STRUCTURE = "structure"


class ObjectStatus(Enum):
    """Status of physical objects."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"
    ERROR = "error"
    OFFLINE = "offline"
    INITIALIZING = "initializing"
    SHUTTING_DOWN = "shutting_down"
    CALIBRATING = "calibrating"


class MaterialType(Enum):
    """Types of materials for physical objects."""

    METAL = "metal"
    PLASTIC = "plastic"
    WOOD = "wood"
    GLASS = "glass"
    CERAMIC = "ceramic"
    COMPOSITE = "composite"
    LIQUID = "liquid"
    GAS = "gas"
    UNKNOWN = "unknown"


class EventType(Enum):
    """Types of events for object lifecycle."""

    CREATED = "created"
    MOVED = "moved"
    STATUS_CHANGED = "status_changed"
    PROPERTY_UPDATED = "property_updated"
    COLLISION = "collision"
    DESTROYED = "destroyed"
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"


@dataclass
class MaterialProperties:
    """Material properties for physics calculations."""

    density: float  # kg/m³
    elasticity: float  # Young's modulus in Pa
    thermal_conductivity: float  # W/(m⋅K)
    specific_heat: float  # J/(kg⋅K)
    melting_point: float  # K
    friction_coefficient: float = 0.5
    restitution: float = 0.5  # Coefficient of restitution

    @classmethod
    def from_material_type(cls, material_type: MaterialType) -> MaterialProperties:
        """Create material properties from material type."""
        properties_map = {
            MaterialType.METAL: cls(7850, 200e9, 45, 500, 1811, 0.4, 0.3),
            MaterialType.PLASTIC: cls(1200, 2e9, 0.2, 1500, 373, 0.6, 0.8),
            MaterialType.WOOD: cls(600, 12e9, 0.15, 1700, 573, 0.7, 0.4),
            MaterialType.GLASS: cls(2500, 70e9, 1.0, 840, 1973, 0.9, 0.1),
            MaterialType.CERAMIC: cls(3000, 400e9, 2.0, 800, 2273, 0.8, 0.2),
            MaterialType.COMPOSITE: cls(1500, 50e9, 1.5, 1200, 873, 0.5, 0.5),
            MaterialType.LIQUID: cls(1000, 0.1e9, 0.6, 4200, 373, 0.1, 0.9),
            MaterialType.GAS: cls(1.2, 0.001e9, 0.025, 1000, 20, 0.01, 0.95),
            MaterialType.UNKNOWN: cls(1000, 10e9, 1.0, 1000, 1000, 0.5, 0.5),
        }
        return properties_map.get(material_type, properties_map[MaterialType.UNKNOWN])


@dataclass
class ObjectEvent:
    """Event in object lifecycle."""

    event_type: EventType
    object_id: str
    timestamp: float = field(default_factory=time.time)
    data: dict[str, Any] = field(default_factory=dict)
    source: str | None = None


@dataclass
class SpatialIndex:
    """Spatial indexing for efficient object queries."""

    grid_size: float = 10.0
    _grid: dict[tuple[int, int, int], set[str]] = field(default_factory=dict)
    _object_locations: dict[str, tuple[int, int, int]] = field(default_factory=dict)
    _object_coordinates: dict[str, tuple[float, float, float]] = field(
        default_factory=dict
    )

    def add_object(self, object_id: str, x: float, y: float, z: float) -> None:
        """Add object to spatial index."""
        grid_key = (
            int(x // self.grid_size),
            int(y // self.grid_size),
            int(z // self.grid_size),
        )

        # Remove from old location if exists
        if object_id in self._object_locations:
            old_key = self._object_locations[object_id]
            if old_key in self._grid:
                self._grid[old_key].discard(object_id)
                if not self._grid[old_key]:
                    del self._grid[old_key]

        # Add to new location
        if grid_key not in self._grid:
            self._grid[grid_key] = set()
        self._grid[grid_key].add(object_id)
        self._object_locations[object_id] = grid_key
        self._object_coordinates[object_id] = (x, y, z)

    def remove_object(self, object_id: str) -> None:
        """Remove object from spatial index."""
        if object_id in self._object_locations:
            grid_key = self._object_locations.pop(object_id)
            self._object_coordinates.pop(object_id, None)
            if grid_key in self._grid:
                self._grid[grid_key].discard(object_id)
                if not self._grid[grid_key]:
                    del self._grid[grid_key]

    def get_nearby_cells(self, x: float, y: float, z: float, radius: float) -> set[str]:
        """Get object IDs within the specified radius, using spatial indexing for efficiency."""
        nearby_objects: set[str] = set()
        grid_radius = math.ceil(radius / self.grid_size)
        center_x, center_y, center_z = (
            int(x // self.grid_size),
            int(y // self.grid_size),
            int(z // self.grid_size),
        )

        for dx in range(-grid_radius, grid_radius + 1):
            for dy in range(-grid_radius, grid_radius + 1):
                for dz in range(-grid_radius, grid_radius + 1):
                    grid_key = (center_x + dx, center_y + dy, center_z + dz)
                    if grid_key in self._grid:
                        # Check actual distance for objects in this grid cell
                        for obj_id in self._grid[grid_key]:
                            if obj_id in self._object_coordinates:
                                ox, oy, oz = self._object_coordinates[obj_id]
                                distance = math.sqrt(
                                    (ox - x) ** 2 + (oy - y) ** 2 + (oz - z) ** 2
                                )
                                if distance <= radius:
                                    nearby_objects.add(obj_id)

        return nearby_objects


@dataclass
class PhysicalObject:
    """Represents a physical object in the system."""

    id: str
    name: str
    object_type: ObjectType
    location: tuple[float, float, float]  # x, y, z coordinates
    properties: dict[str, Any] = field(default_factory=dict)
    status: ObjectStatus = ObjectStatus.ACTIVE
    created_at: float = field(default_factory=time.time)
    last_updated: float = field(default_factory=time.time)

    # New advanced properties
    material: MaterialType = MaterialType.UNKNOWN
    material_properties: MaterialProperties | None = None
    mass: float = 1.0  # kg
    volume: float = 1.0  # m³
    temperature: float = 293.15  # K (20°C)
    connections: set[str] = field(default_factory=set)  # Connected object IDs
    tags: set[str] = field(default_factory=set)  # Tags for categorization
    metadata: dict[str, Any] = field(default_factory=dict)  # Extended metadata

    def __post_init__(self) -> None:
        """Initialize material properties if not provided."""
        if self.material_properties is None:
            self.material_properties = MaterialProperties.from_material_type(
                self.material
            )

    @property
    def density(self) -> float:
        """Calculate density from mass and volume."""
        return self.mass / self.volume if self.volume > 0 else 0.0

    def update_location(self, x: float, y: float, z: float) -> None:
        """Update object location."""
        self.location = (x, y, z)
        self.last_updated = time.time()

    def update_status(self, status: ObjectStatus) -> None:
        """Update object status."""
        self.status = status
        self.last_updated = time.time()

    def distance_to(self, other_object: PhysicalObject) -> float:
        """Calculate distance to another object."""
        x1, y1, z1 = self.location
        x2, y2, z2 = other_object.location
        return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2 + (z2 - z1) ** 2)

    def distance_to_point(self, x: float, y: float, z: float) -> float:
        """Calculate distance to a point."""
        x1, y1, z1 = self.location
        return math.sqrt((x - x1) ** 2 + (y - y1) ** 2 + (z - z1) ** 2)

    def is_within_range(
        self, x: float, y: float, z: float, max_distance: float
    ) -> bool:
        """Check if object is within range of a point."""
        return self.distance_to_point(x, y, z) <= max_distance

    def add_property(self, key: str, value: Any) -> None:
        """Add or update a property."""
        self.properties[key] = value
        self.last_updated = time.time()

    def remove_property(self, key: str) -> Any | None:
        """Remove a property and return its value."""
        if key in self.properties:
            value = self.properties.pop(key)
            self.last_updated = time.time()
            return value
        return None

    def add_tag(self, tag: str) -> None:
        """Add a tag to the object."""
        self.tags.add(tag)
        self.last_updated = time.time()

    def remove_tag(self, tag: str) -> bool:
        """Remove a tag from the object."""
        if tag in self.tags:
            self.tags.remove(tag)
            self.last_updated = time.time()
            return True
        return False

    def has_tag(self, tag: str) -> bool:
        """Check if object has a specific tag."""
        return tag in self.tags

    def connect_to(self, other_object_id: str) -> None:
        """Create a connection to another object."""
        self.connections.add(other_object_id)
        self.last_updated = time.time()

    def disconnect_from(self, other_object_id: str) -> bool:
        """Remove connection to another object."""
        if other_object_id in self.connections:
            self.connections.remove(other_object_id)
            self.last_updated = time.time()
            return True
        return False

    def is_connected_to(self, other_object_id: str) -> bool:
        """Check if connected to another object."""
        return other_object_id in self.connections

    def update_temperature(self, new_temperature: float) -> None:
        """Update object temperature."""
        self.temperature = new_temperature
        self.last_updated = time.time()

    def calculate_thermal_energy(self) -> float:
        """Calculate thermal energy based on mass, specific heat, and temperature."""
        if self.material_properties:
            return (
                self.mass
                * self.material_properties.specific_heat
                * (self.temperature - 273.15)
            )
        return 0.0

    def get_age(self) -> float:
        """Get age of object in seconds."""
        return time.time() - self.created_at

    def time_since_update(self) -> float:
        """Get time since last update in seconds."""
        return time.time() - self.last_updated

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "id": self.id,
            "name": self.name,
            "object_type": self.object_type.value,
            "location": self.location,
            "properties": self.properties,
            "status": self.status.value,
            "created_at": self.created_at,
            "last_updated": self.last_updated,
            "material": self.material.value,
            "mass": self.mass,
            "volume": self.volume,
            "temperature": self.temperature,
            "connections": list(self.connections),
            "tags": list(self.tags),
            "metadata": self.metadata,
        }
