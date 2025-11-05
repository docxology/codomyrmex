"""Core physical object management system."""

import json
import logging
import math
import threading
import time
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Optional

logger = logging.getLogger(__name__)


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
    def from_material_type(cls, material_type: MaterialType) -> "MaterialProperties":
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
    source: Optional[str] = None


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
        nearby_objects = set()
        grid_radius = int(math.ceil(radius / self.grid_size))
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
    material_properties: Optional[MaterialProperties] = None
    mass: float = 1.0  # kg
    volume: float = 1.0  # m³
    temperature: float = 293.15  # K (20°C)
    connections: set[str] = field(default_factory=set)  # Connected object IDs
    tags: set[str] = field(default_factory=set)  # Tags for categorization
    metadata: dict[str, Any] = field(default_factory=dict)  # Extended metadata

    def __post_init__(self):
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

    def distance_to(self, other_object: "PhysicalObject") -> float:
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

    def remove_property(self, key: str) -> Optional[Any]:
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


class ObjectRegistry:
    """Registry for managing physical objects."""

    def __init__(self, spatial_grid_size: float = 10.0):
        """  Init  .

            Args:        spatial_grid_size: Unique identifier.
            """
        self.objects: dict[str, PhysicalObject] = {}
        self._location_index: dict[tuple[int, int, int], set[str]] = (
            {}
        )  # Legacy grid-based index
        self.spatial_index = SpatialIndex(grid_size=spatial_grid_size)
        self.event_handlers: dict[EventType, list[Callable[[ObjectEvent], None]]] = (
            defaultdict(list)
        )
        self.event_history: list[ObjectEvent] = []
        self.max_event_history = 10000
        self._lock = threading.RLock()  # Thread safety

    def register_object(self, obj: PhysicalObject) -> None:
        """Register a physical object."""
        with self._lock:
            self.objects[obj.id] = obj
            self._update_location_index(obj)
            self.spatial_index.add_object(obj.id, *obj.location)

            # Emit created event
            self._emit_event(
                ObjectEvent(
                    event_type=EventType.CREATED,
                    object_id=obj.id,
                    data={
                        "object_type": obj.object_type.value,
                        "location": obj.location,
                    },
                )
            )

            logger.info(f"Registered physical object: {obj.id}")

    def unregister_object(self, object_id: str) -> Optional[PhysicalObject]:
        """Unregister a physical object."""
        if object_id in self.objects:
            obj = self.objects.pop(object_id)
            self._remove_from_location_index(obj)
            logger.info(f"Unregistered physical object: {object_id}")
            return obj
        return None

    def get_object(self, object_id: str) -> Optional[PhysicalObject]:
        """Get a physical object by ID."""
        return self.objects.get(object_id)

    def get_objects_by_type(self, object_type: ObjectType) -> list[PhysicalObject]:
        """Get all objects of a specific type."""
        return [obj for obj in self.objects.values() if obj.object_type == object_type]

    def get_objects_in_area(
        self, x: float, y: float, z: float, radius: float
    ) -> list[PhysicalObject]:
        """Get objects within a spherical area."""
        nearby_objects = []
        center_x, center_y, center_z = int(x), int(y), int(z)

        # Check surrounding grid cells
        for dx in range(-int(radius), int(radius) + 1):
            for dy in range(-int(radius), int(radius) + 1):
                for dz in range(-int(radius), int(radius) + 1):
                    grid_key = (center_x + dx, center_y + dy, center_z + dz)
                    if grid_key in self._location_index:
                        for obj_id in self._location_index[grid_key]:
                            obj = self.objects[obj_id]
                            distance = (
                                (obj.location[0] - x) ** 2
                                + (obj.location[1] - y) ** 2
                                + (obj.location[2] - z) ** 2
                            ) ** 0.5
                            if distance <= radius:
                                nearby_objects.append(obj)

        return nearby_objects

    def get_objects_by_status(self, status: ObjectStatus) -> list[PhysicalObject]:
        """Get all objects with a specific status."""
        return [obj for obj in self.objects.values() if obj.status == status]

    def get_objects_by_property(
        self, property_key: str, property_value: Any
    ) -> list[PhysicalObject]:
        """Get objects with a specific property value."""
        return [
            obj
            for obj in self.objects.values()
            if property_key in obj.properties
            and obj.properties[property_key] == property_value
        ]

    def find_nearest_object(
        self, x: float, y: float, z: float, object_type: Optional[ObjectType] = None
    ) -> Optional[PhysicalObject]:
        """Find the nearest object to a point, optionally filtered by type."""
        min_distance = float("inf")
        nearest_object = None

        for obj in self.objects.values():
            if object_type is None or obj.object_type == object_type:
                distance = obj.distance_to_point(x, y, z)
                if distance < min_distance:
                    min_distance = distance
                    nearest_object = obj

        return nearest_object

    def check_collisions(
        self, collision_distance: float = 1.0
    ) -> list[tuple[PhysicalObject, PhysicalObject]]:
        """Find all object pairs that are within collision distance."""
        collisions = []
        objects_list = list(self.objects.values())

        for i, obj1 in enumerate(objects_list):
            for obj2 in objects_list[i + 1 :]:
                if obj1.distance_to(obj2) <= collision_distance:
                    collisions.append((obj1, obj2))

        return collisions

    def group_objects_by_distance(
        self, max_group_distance: float = 5.0
    ) -> list[list[PhysicalObject]]:
        """Group objects that are close to each other."""
        ungrouped = list(self.objects.values())
        groups = []

        while ungrouped:
            # Start a new group with any remaining object
            current_obj = ungrouped.pop(0)
            current_group = [current_obj]

            # Find all objects within distance of any object in current group
            changed = True
            while changed:
                changed = False
                to_remove = []

                for i, obj in enumerate(ungrouped):
                    for group_obj in current_group:
                        if obj.distance_to(group_obj) <= max_group_distance:
                            current_group.append(obj)
                            to_remove.append(i)
                            changed = True
                            break

                # Remove from ungrouped list (in reverse order to maintain indices)
                for i in reversed(to_remove):
                    ungrouped.pop(i)

            groups.append(current_group)

        return groups

    def _emit_event(self, event: ObjectEvent) -> None:
        """Emit an event to registered handlers."""
        self.event_history.append(event)

        # Limit event history size
        if len(self.event_history) > self.max_event_history:
            self.event_history = self.event_history[-self.max_event_history :]

        # Call event handlers
        for handler in self.event_handlers[event.event_type]:
            try:
                handler(event)
            except Exception as e:
                logger.error(f"Error in event handler: {e}")

    def add_event_handler(
        self, event_type: EventType, handler: Callable[[ObjectEvent], None]
    ) -> None:
        """Add an event handler for a specific event type."""
        with self._lock:
            self.event_handlers[event_type].append(handler)

    def remove_event_handler(
        self, event_type: EventType, handler: Callable[[ObjectEvent], None]
    ) -> bool:
        """Remove an event handler."""
        with self._lock:
            try:
                self.event_handlers[event_type].remove(handler)
                return True
            except ValueError:
                return False

    def get_events(
        self,
        event_type: Optional[EventType] = None,
        object_id: Optional[str] = None,
        since: Optional[float] = None,
    ) -> list[ObjectEvent]:
        """Get events filtered by type, object ID, and/or timestamp."""
        events = self.event_history

        if event_type:
            events = [e for e in events if e.event_type == event_type]

        if object_id:
            events = [e for e in events if e.object_id == object_id]

        if since:
            events = [e for e in events if e.timestamp >= since]

        return events

    def get_objects_by_tags(
        self, tags: set[str], match_all: bool = True
    ) -> list[PhysicalObject]:
        """Get objects that have specific tags."""
        matching_objects = []

        for obj in self.objects.values():
            if match_all:
                if tags.issubset(obj.tags):
                    matching_objects.append(obj)
            else:
                if obj.tags.intersection(tags):
                    matching_objects.append(obj)

        return matching_objects

    def get_network_topology(self) -> dict[str, list[str]]:
        """Get network topology of connected objects."""
        topology = {}

        for obj_id, obj in self.objects.items():
            topology[obj_id] = list(obj.connections)

        return topology

    def find_path_through_network(
        self, start_id: str, end_id: str, max_hops: int = 10
    ) -> Optional[list[str]]:
        """Find path between objects through network connections (BFS)."""
        if start_id not in self.objects or end_id not in self.objects:
            return None

        if start_id == end_id:
            return [start_id]

        visited = set()
        queue = [(start_id, [start_id])]

        while queue:
            current_id, path = queue.pop(0)

            if len(path) > max_hops:
                continue

            if current_id in visited:
                continue

            visited.add(current_id)
            current_obj = self.objects[current_id]

            for connected_id in current_obj.connections:
                if connected_id == end_id:
                    return path + [connected_id]

                if connected_id not in visited and connected_id in self.objects:
                    queue.append((connected_id, path + [connected_id]))

        return None

    def analyze_network_metrics(self) -> dict[str, Any]:
        """Analyze network topology metrics."""
        total_objects = len(self.objects)
        total_connections = sum(len(obj.connections) for obj in self.objects.values())

        # Calculate clustering coefficient and other metrics
        clustering_coefficients = []
        degrees = []

        for obj in self.objects.values():
            degree = len(obj.connections)
            degrees.append(degree)

            if degree < 2:
                clustering_coefficients.append(0.0)
                continue

            # Count triangles
            triangles = 0
            possible_triangles = degree * (degree - 1) // 2

            connections_list = list(obj.connections)
            for i, conn1 in enumerate(connections_list):
                for conn2 in connections_list[i + 1 :]:
                    if (
                        conn1 in self.objects
                        and conn2 in self.objects
                        and conn2 in self.objects[conn1].connections
                    ):
                        triangles += 1

            clustering_coeff = (
                triangles / possible_triangles if possible_triangles > 0 else 0.0
            )
            clustering_coefficients.append(clustering_coeff)

        return {
            "total_objects": total_objects,
            "total_connections": total_connections // 2,  # Assuming bidirectional
            "average_degree": sum(degrees) / len(degrees) if degrees else 0,
            "max_degree": max(degrees) if degrees else 0,
            "min_degree": min(degrees) if degrees else 0,
            "average_clustering": (
                sum(clustering_coefficients) / len(clustering_coefficients)
                if clustering_coefficients
                else 0
            ),
            "density": (
                (total_connections / 2) / (total_objects * (total_objects - 1) / 2)
                if total_objects > 1
                else 0
            ),
        }

    def _update_location_index(self, obj: PhysicalObject) -> None:
        """Update the location index for an object."""
        grid_x, grid_y, grid_z = (
            int(obj.location[0]),
            int(obj.location[1]),
            int(obj.location[2]),
        )
        grid_key = (grid_x, grid_y, grid_z)

        if grid_key not in self._location_index:
            self._location_index[grid_key] = set()
        self._location_index[grid_key].add(obj.id)

    def _remove_from_location_index(self, obj: PhysicalObject) -> None:
        """Remove an object from the location index."""
        grid_x, grid_y, grid_z = (
            int(obj.location[0]),
            int(obj.location[1]),
            int(obj.location[2]),
        )
        grid_key = (grid_x, grid_y, grid_z)

        if grid_key in self._location_index:
            self._location_index[grid_key].discard(obj.id)
            if not self._location_index[grid_key]:
                del self._location_index[grid_key]

    def save_to_file(self, file_path: str | Path) -> None:
        """Save registry to file."""
        data = {
            "objects": [obj.to_dict() for obj in self.objects.values()],
            "metadata": {
                "total_objects": len(self.objects),
                "exported_at": time.time(),
            },
        }

        Path(file_path).write_text(json.dumps(data, indent=2))

    def load_from_file(self, file_path: str | Path) -> None:
        """Load registry from file."""
        if not Path(file_path).exists():
            return

        data = json.loads(Path(file_path).read_text())

        for obj_data in data.get("objects", []):
            obj = PhysicalObject(
                id=obj_data["id"],
                name=obj_data["name"],
                object_type=ObjectType(obj_data["object_type"]),
                location=tuple(obj_data["location"]),
                properties=obj_data.get("properties", {}),
                status=ObjectStatus(obj_data["status"]),
                created_at=obj_data["created_at"],
                last_updated=obj_data["last_updated"],
            )
            self.register_object(obj)


class PhysicalObjectManager:
    """Main manager for physical object operations."""

    def __init__(self):
        self.registry = ObjectRegistry()
        self._active_simulations = set()

    def create_object(
        self,
        object_id: str,
        name: str,
        object_type: ObjectType,
        x: float,
        y: float,
        z: float,
        material: MaterialType = MaterialType.UNKNOWN,
        mass: float = 1.0,
        volume: float = 1.0,
        temperature: float = 293.15,
        **properties,
    ) -> PhysicalObject:
        """Create a new physical object."""
        obj = PhysicalObject(
            id=object_id,
            name=name,
            object_type=object_type,
            location=(x, y, z),
            properties=properties,
            material=material,
            mass=mass,
            volume=volume,
            temperature=temperature,
        )
        self.registry.register_object(obj)
        return obj

    def get_object_status(self, object_id: str) -> Optional[ObjectStatus]:
        """Get the status of an object."""
        obj = self.registry.get_object(object_id)
        return obj.status if obj else None

    def update_object_location(
        self, object_id: str, x: float, y: float, z: float
    ) -> bool:
        """Update an object's location."""
        obj = self.registry.get_object(object_id)
        if obj:
            obj.update_location(x, y, z)
            self.registry._update_location_index(obj)
            return True
        return False

    def get_nearby_objects(
        self, x: float, y: float, z: float, radius: float
    ) -> list[PhysicalObject]:
        """Get objects near a location."""
        return self.registry.get_objects_in_area(x, y, z, radius)

    def get_objects_by_type(self, object_type: ObjectType) -> list[PhysicalObject]:
        """Get all objects of a specific type."""
        return self.registry.get_objects_by_type(object_type)

    def save_state(self, file_path: str | Path) -> None:
        """Save the current state to file."""
        self.registry.save_to_file(file_path)

    def load_state(self, file_path: str | Path) -> None:
        """Load state from file."""
        self.registry.load_from_file(file_path)

    def get_statistics(self) -> dict[str, Any]:
        """Get statistics about managed objects."""
        objects_by_type = {}
        for obj_type in ObjectType:
            objects_by_type[obj_type.value] = len(
                self.registry.get_objects_by_type(obj_type)
            )

        objects_by_status = {}
        for obj in self.registry.objects.values():
            status = obj.status.value
            objects_by_status[status] = objects_by_status.get(status, 0) + 1

        return {
            "total_objects": len(self.registry.objects),
            "objects_by_type": objects_by_type,
            "objects_by_status": objects_by_status,
            "active_simulations": len(self._active_simulations),
        }

    def batch_update_status(
        self, object_ids: list[str], new_status: ObjectStatus
    ) -> int:
        """Update status for multiple objects. Returns number of objects updated."""
        updated_count = 0
        for obj_id in object_ids:
            obj = self.registry.get_object(obj_id)
            if obj:
                obj.update_status(new_status)
                updated_count += 1
        return updated_count

    def batch_move_objects(self, moves: dict[str, tuple[float, float, float]]) -> int:
        """Move multiple objects. Returns number of objects moved."""
        moved_count = 0
        for obj_id, (x, y, z) in moves.items():
            if self.update_object_location(obj_id, x, y, z):
                moved_count += 1
        return moved_count

    def find_path_between_objects(
        self, start_object_id: str, end_object_id: str, max_steps: int = 10
    ) -> Optional[list[PhysicalObject]]:
        """Find a path between two objects using nearby objects as waypoints."""
        start_obj = self.registry.get_object(start_object_id)
        end_obj = self.registry.get_object(end_object_id)

        if not start_obj or not end_obj:
            return None

        # Simple greedy pathfinding
        path = [start_obj]
        current = start_obj

        for _ in range(max_steps):
            if current.distance_to(end_obj) <= 1.0:  # Close enough
                path.append(end_obj)
                return path

            # Find next waypoint - nearest object that's closer to destination
            nearby = self.get_nearby_objects(*current.location, 5.0)
            best_next = None
            best_distance_to_end = float("inf")

            for obj in nearby:
                if obj.id not in [p.id for p in path]:  # Avoid cycles
                    distance_to_end = obj.distance_to(end_obj)
                    if distance_to_end < best_distance_to_end:
                        best_distance_to_end = distance_to_end
                        best_next = obj

            if best_next:
                path.append(best_next)
                current = best_next
            else:
                break

        return None  # No path found

    def calculate_center_of_mass(
        self, object_ids: Optional[list[str]] = None
    ) -> tuple[float, float, float]:
        """Calculate center of mass for specified objects or all objects."""
        if object_ids is None:
            objects = list(self.registry.objects.values())
        else:
            objects = [self.registry.get_object(obj_id) for obj_id in object_ids]
            objects = [obj for obj in objects if obj is not None]

        if not objects:
            return (0.0, 0.0, 0.0)

        total_x = sum(obj.location[0] for obj in objects)
        total_y = sum(obj.location[1] for obj in objects)
        total_z = sum(obj.location[2] for obj in objects)
        count = len(objects)

        return (total_x / count, total_y / count, total_z / count)

    def detect_object_clusters(
        self, cluster_radius: float = 3.0, min_cluster_size: int = 2
    ) -> list[list[PhysicalObject]]:
        """Detect clusters of objects within a specified radius."""
        groups = self.registry.group_objects_by_distance(cluster_radius)
        return [group for group in groups if len(group) >= min_cluster_size]

    def get_boundary_box(
        self, object_ids: Optional[list[str]] = None
    ) -> dict[str, tuple[float, float]]:
        """Get the bounding box containing all or specified objects."""
        if object_ids is None:
            objects = list(self.registry.objects.values())
        else:
            objects = [self.registry.get_object(obj_id) for obj_id in object_ids]
            objects = [obj for obj in objects if obj is not None]

        if not objects:
            return {"x": (0.0, 0.0), "y": (0.0, 0.0), "z": (0.0, 0.0)}

        x_coords = [obj.location[0] for obj in objects]
        y_coords = [obj.location[1] for obj in objects]
        z_coords = [obj.location[2] for obj in objects]

        return {
            "x": (min(x_coords), max(x_coords)),
            "y": (min(y_coords), max(y_coords)),
            "z": (min(z_coords), max(z_coords)),
        }


__all__ = [
    "ObjectType",
    "ObjectStatus",
    "MaterialType",
    "EventType",
    "PhysicalObject",
    "ObjectRegistry",
    "PhysicalObjectManager",
    "MaterialProperties",
    "ObjectEvent",
    "SpatialIndex",
]
