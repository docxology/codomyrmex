# Codomyrmex Agents — src/codomyrmex/physical_management

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: December 2025

## Purpose

Specialized Layer module providing physical object management, simulation, and sensor integration capabilities for the Codomyrmex platform. This module enables physical computing, IoT device management, and real-world object tracking through simulation and sensor frameworks.

The physical_management module serves as the physical computing layer, bridging digital systems with real-world physical objects and environments.

## Module Overview

### Key Capabilities
- **Physical Object Management**: Registration, tracking, and lifecycle management of physical objects
- **Physics Simulation**: Real-time physics simulation with forces, constraints, and collisions
- **Sensor Integration**: IoT sensor data collection, processing, and analytics
- **Spatial Indexing**: Efficient spatial queries and proximity calculations
- **Network Analysis**: Object relationship modeling and pathfinding
- **Streaming Analytics**: Real-time data processing and predictive analytics

### Key Features
- Multi-object spatial indexing and querying
- Physics-based simulation with collision detection
- Sensor data calibration and drift detection
- Real-time streaming analytics and alerting
- Object relationship modeling and network analysis
- Material properties and thermal simulation

## Function Signatures

### PhysicalObjectManager Class Methods

```python
def __init__(self, spatial_grid_size: float = 10.0) -> None
```

Initialize the physical object manager.

**Parameters:**
- `spatial_grid_size` (float): Size of spatial grid cells for indexing. Defaults to 10.0

**Returns:** None

```python
def register_object(self, obj: PhysicalObject) -> None
```

Register a physical object with the manager.

**Parameters:**
- `obj` (PhysicalObject): Physical object to register

**Returns:** None

```python
def unregister_object(self, object_id: str) -> Optional[PhysicalObject]
```

Unregister a physical object from the manager.

**Parameters:**
- `object_id` (str): ID of the object to unregister

**Returns:** `Optional[PhysicalObject]` - The unregistered object or None

```python
def get_object(self, object_id: str) -> Optional[PhysicalObject]
```

Get a physical object by ID.

**Parameters:**
- `object_id` (str): ID of the object to retrieve

**Returns:** `Optional[PhysicalObject]` - The physical object or None

```python
def get_objects_by_type(self, object_type: ObjectType) -> list[PhysicalObject]
```

Get all objects of a specific type.

**Parameters:**
- `object_type` (ObjectType): Type of objects to retrieve

**Returns:** `list[PhysicalObject]` - List of objects matching the type

```python
def get_objects_in_area(
    self, center_x: float, center_y: float, center_z: float, radius: float
) -> list[PhysicalObject]
```

Get all objects within a spherical area.

**Parameters:**
- `center_x` (float): X coordinate of area center
- `center_y` (float): Y coordinate of area center
- `center_z` (float): Z coordinate of area center
- `radius` (float): Radius of the search area

**Returns:** `list[PhysicalObject]` - List of objects within the area

```python
def get_objects_by_status(self, status: ObjectStatus) -> list[PhysicalObject]
```

Get all objects with a specific status.

**Parameters:**
- `status` (ObjectStatus): Status to filter by

**Returns:** `list[PhysicalObject]` - List of objects with matching status

```python
def get_objects_by_property(
    self, property_key: str, property_value: Any
) -> list[PhysicalObject]
```

Get objects by custom property value.

**Parameters:**
- `property_key` (str): Property key to search for
- `property_value` (Any): Property value to match

**Returns:** `list[PhysicalObject]` - List of objects with matching property

```python
def find_nearest_object(
    self, x: float, y: float, z: float, object_type: Optional[ObjectType] = None
) -> Optional[PhysicalObject]
```

Find the nearest object to a point.

**Parameters:**
- `x` (float): X coordinate
- `y` (float): Y coordinate
- `z` (float): Z coordinate
- `object_type` (Optional[ObjectType]): Filter by object type

**Returns:** `Optional[PhysicalObject]` - Nearest object or None

```python
def check_collisions(
    self, object_id: str, collision_radius: float = 1.0
) -> list[str]
```

Check for collisions involving an object.

**Parameters:**
- `object_id` (str): ID of the object to check collisions for
- `collision_radius` (float): Collision detection radius. Defaults to 1.0

**Returns:** `list[str]` - List of object IDs that collide with the given object

```python
def add_event_handler(
    self, event_type: EventType, handler: Callable[[ObjectEvent], None]
) -> None
```

Add an event handler for object events.

**Parameters:**
- `event_type` (EventType): Type of event to handle
- `handler` (Callable[[ObjectEvent], None]): Event handler function

**Returns:** None

```python
def remove_event_handler(
    self, event_type: EventType, handler: Callable[[ObjectEvent], None]
) -> bool
```

Remove an event handler.

**Parameters:**
- `event_type` (EventType): Type of event
- `handler` (Callable[[ObjectEvent], None]): Handler function to remove

**Returns:** `bool` - True if handler was removed

```python
def get_events(
    self,
    event_type: Optional[EventType] = None,
    object_id: Optional[str] = None,
    time_range: Optional[tuple[float, float]] = None
) -> list[ObjectEvent]
```

Get historical events with optional filtering.

**Parameters:**
- `event_type` (Optional[EventType]): Filter by event type
- `object_id` (Optional[str]): Filter by object ID
- `time_range` (Optional[tuple[float, float]]): Filter by time range (start, end)

**Returns:** `list[ObjectEvent]` - List of matching events

```python
def get_objects_by_tags(self, tags: list[str], match_all: bool = False) -> list[PhysicalObject]
```

Get objects by tags.

**Parameters:**
- `tags` (list[str]): List of tags to match
- `match_all` (bool): Whether all tags must match. Defaults to False

**Returns:** `list[PhysicalObject]` - List of objects with matching tags

```python
def get_network_topology(self) -> dict[str, list[str]]
```

Get the network topology of object connections.

**Returns:** `dict[str, list[str]]` - Dictionary mapping object IDs to connected object IDs

```python
def find_path_through_network(
    self, start_object_id: str, end_object_id: str
) -> Optional[list[str]]
```

Find a path between two objects through the network.

**Parameters:**
- `start_object_id` (str): Starting object ID
- `end_object_id` (str): Ending object ID

**Returns:** `Optional[list[str]]` - Path as list of object IDs or None if no path found

```python
def analyze_network_metrics(self) -> dict[str, Any]
```

Analyze network topology metrics.

**Returns:** `dict[str, Any]` - Network analysis metrics

```python
def save_to_file(self, file_path: str | Path) -> None
```

Save the object registry to a file.

**Parameters:**
- `file_path` (str | Path): Path to save the registry

**Returns:** None

```python
def load_from_file(self, file_path: str | Path) -> None
```

Load the object registry from a file.

**Parameters:**
- `file_path` (str | Path): Path to load the registry from

**Returns:** None

### PhysicalObjectManager (High-Level Interface) Methods

```python
def __init__(self) -> None
```

Initialize the high-level physical object manager.

**Returns:** None

```python
def create_object(
    self,
    object_id: str,
    name: str,
    object_type: ObjectType,
    x: float = 0.0,
    y: float = 0.0,
    z: float = 0.0,
    material_type: MaterialType = MaterialType.GENERIC,
) -> PhysicalObject
```

Create a new physical object.

**Parameters:**
- `object_id` (str): Unique identifier for the object
- `name` (str): Human-readable name
- `object_type` (ObjectType): Type of the object
- `x` (float): Initial X position. Defaults to 0.0
- `y` (float): Initial Y position. Defaults to 0.0
- `z` (float): Initial Z position. Defaults to 0.0
- `material_type` (MaterialType): Material type. Defaults to MaterialType.GENERIC

**Returns:** `PhysicalObject` - Created physical object

```python
def get_object_status(self, object_id: str) -> Optional[ObjectStatus]
```

Get the status of a physical object.

**Parameters:**
- `object_id` (str): ID of the object

**Returns:** `Optional[ObjectStatus]` - Object status or None

```python
def update_object_location(
    self, object_id: str, x: float, y: float, z: float
) -> bool
```

Update the location of a physical object.

**Parameters:**
- `object_id` (str): ID of the object
- `x` (float): New X coordinate
- `y` (float): New Y coordinate
- `z` (float): New Z coordinate

**Returns:** `bool` - True if update successful

```python
def get_nearby_objects(
    self, x: float, y: float, z: float, radius: float
) -> list[PhysicalObject]
```

Get objects within a radius of a point.

**Parameters:**
- `x` (float): Center X coordinate
- `y` (float): Center Y coordinate
- `z` (float): Center Z coordinate
- `radius` (float): Search radius

**Returns:** `list[PhysicalObject]` - List of nearby objects

```python
def batch_update_status(
    self, updates: dict[str, ObjectStatus]
) -> int
```

Batch update status for multiple objects.

**Parameters:**
- `updates` (dict[str, ObjectStatus]): Dictionary mapping object IDs to new statuses

**Returns:** `int` - Number of objects updated

```python
def batch_move_objects(self, moves: dict[str, tuple[float, float, float]]) -> int
```

Batch move multiple objects to new positions.

**Parameters:**
- `moves` (dict[str, tuple[float, float, float]]): Dictionary mapping object IDs to new positions

**Returns:** `int` - Number of objects moved

```python
def find_path_between_objects(
    self, start_id: str, end_id: str
) -> Optional[list[str]]
```

Find a path between two objects through the network.

**Parameters:**
- `start_id` (str): Starting object ID
- `end_id` (str): Ending object ID

**Returns:** `Optional[list[str]]` - Path as list of object IDs or None

```python
def calculate_center_of_mass(
    self, object_ids: list[str]
) -> Optional[tuple[float, float, float]]
```

Calculate center of mass for a group of objects.

**Parameters:**
- `object_ids` (list[str]): List of object IDs

**Returns:** `Optional[tuple[float, float, float]]` - Center of mass coordinates or None

```python
def detect_object_clusters(
    self, cluster_radius: float
) -> list[list[str]]
```

Detect clusters of objects based on proximity.

**Parameters:**
- `cluster_radius` (float): Maximum distance for cluster membership

**Returns:** `list[list[str]]` - List of clusters, each containing object IDs

```python
def get_boundary_box(
    self, object_ids: Optional[list[str]] = None
) -> Optional[tuple[tuple[float, float, float], tuple[float, float, float]]]
```

Get the bounding box for objects.

**Parameters:**
- `object_ids` (Optional[list[str]]): Specific object IDs. If None, uses all objects

**Returns:** `Optional[tuple[tuple[float, float, float], tuple[float, float, float]]]` - Min and max coordinates or None

### PhysicsSimulator Class Methods

```python
def __init__(self) -> None
```

Initialize the physics simulator.

**Returns:** None

```python
def add_force_field(self, force_field: ForceField) -> None
```

Add a force field to the simulation.

**Parameters:**
- `force_field` (ForceField): Force field to add

**Returns:** None

```python
def add_constraint(self, constraint: Constraint) -> None
```

Add a constraint to the simulation.

**Parameters:**
- `constraint` (Constraint): Constraint to add

**Returns:** None

```python
def register_object(
    self,
    object_id: str,
    position: Vector3D,
    velocity: Vector3D = None,
    mass: float = 1.0
) -> None
```

Register an object for physics simulation.

**Parameters:**
- `object_id` (str): Unique object identifier
- `position` (Vector3D): Initial position
- `velocity` (Vector3D): Initial velocity. Defaults to zero vector
- `mass` (float): Object mass. Defaults to 1.0

**Returns:** None

```python
def update_physics(self, delta_time: float) -> None
```

Update the physics simulation by one time step.

**Parameters:**
- `delta_time` (float): Time step duration

**Returns:** None

```python
def get_object_state(self, object_id: str) -> Optional[dict[str, Any]]
```

Get the current state of a simulated object.

**Parameters:**
- `object_id` (str): Object identifier

**Returns:** `Optional[dict[str, Any]]` - Object state or None if not found

```python
def set_object_position(self, object_id: str, position: Vector3D) -> bool
```

Set the position of a simulated object.

**Parameters:**
- `object_id` (str): Object identifier
- `position` (Vector3D): New position

**Returns:** `bool` - True if position set successfully

```python
def get_simulation_stats(self) -> dict[str, Any]
```

Get statistics about the physics simulation.

**Returns:** `dict[str, Any]` - Simulation statistics

```python
def apply_impulse(self, object_id: str, impulse: Vector3D) -> bool
```

Apply an impulse to a simulated object.

**Parameters:**
- `object_id` (str): Object identifier
- `impulse` (Vector3D): Impulse vector

**Returns:** `bool` - True if impulse applied successfully

```python
def set_object_velocity(self, object_id: str, velocity: Vector3D) -> bool
```

Set the velocity of a simulated object.

**Parameters:**
- `object_id` (str): Object identifier
- `velocity` (Vector3D): New velocity

**Returns:** `bool` - True if velocity set successfully

```python
def add_spring_constraint(
    self,
    object1_id: str,
    object2_id: str,
    rest_length: float,
    spring_constant: float,
    damping: float = 0.0
) -> None
```

Add a spring constraint between two objects.

**Parameters:**
- `object1_id` (str): First object identifier
- `object2_id` (str): Second object identifier
- `rest_length` (float): Spring rest length
- `spring_constant` (float): Spring constant
- `damping` (float): Damping coefficient. Defaults to 0.0

**Returns:** None

```python
def detect_collisions(self, collision_radius: float = 0.5) -> list[tuple[str, str]]
```

Detect collisions between simulated objects.

**Parameters:**
- `collision_radius` (float): Collision detection radius. Defaults to 0.5

**Returns:** `list[tuple[str, str]]` - List of colliding object pairs

```python
def handle_elastic_collision(self, obj1_id: str, obj2_id: str) -> bool
```

Handle an elastic collision between two objects.

**Parameters:**
- `obj1_id` (str): First object identifier
- `obj2_id` (str): Second object identifier

**Returns:** `bool` - True if collision handled successfully

## Data Structures

### Vector3D
```python
@dataclass
class Vector3D:
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0

    def __add__(self, other: Vector3D) -> Vector3D
    def __sub__(self, other: Vector3D) -> Vector3D
    def __mul__(self, scalar: float) -> Vector3D
    def magnitude(self) -> float
    def normalize(self) -> Vector3D
```

3D vector for spatial calculations.

### PhysicalObject
```python
@dataclass
class PhysicalObject:
    object_id: str
    name: str
    object_type: ObjectType
    material_type: MaterialType
    position: tuple[float, float, float]
    status: ObjectStatus = ObjectStatus.ACTIVE
    properties: dict[str, Any] = None
    tags: set[str] = None
    connections: set[str] = None
    temperature: float = 293.15  # Room temperature in Kelvin
    created_at: float = None
    updated_at: float = None
```

Represents a physical object with properties and state.

### ForceField
```python
class ForceField:
    def calculate_force(self, object_position: Vector3D) -> Vector3D
```

Abstract base class for force fields in physics simulation.

### Constraint
```python
class Constraint:
    def apply_constraint(self, objects: dict[str, dict[str, Any]]) -> None
```

Abstract base class for physics constraints.

### ObjectEvent
```python
@dataclass
class ObjectEvent:
    event_type: EventType
    object_id: str
    timestamp: float
    data: dict[str, Any] = None
```

Represents an event related to a physical object.

## Enums

### ObjectType
```python
class ObjectType(Enum):
    GENERIC = "generic"
    SENSOR = "sensor"
    ACTUATOR = "actuator"
    MACHINE = "machine"
    VEHICLE = "vehicle"
    STRUCTURE = "structure"
    PERSON = "person"
    ROBOT = "robot"
```

Types of physical objects.

### ObjectStatus
```python
class ObjectStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"
    ERROR = "error"
    OFFLINE = "offline"
```

Status states for physical objects.

### MaterialType
```python
class MaterialType(Enum):
    GENERIC = "generic"
    METAL = "metal"
    PLASTIC = "plastic"
    WOOD = "wood"
    GLASS = "glass"
    CERAMIC = "ceramic"
    FABRIC = "fabric"
    LIQUID = "liquid"
```

Material types for physical properties.

### EventType
```python
class EventType(Enum):
    CREATED = "created"
    UPDATED = "updated"
    MOVED = "moved"
    STATUS_CHANGED = "status_changed"
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    COLLISION = "collision"
    TEMPERATURE_CHANGE = "temperature_change"
```

Types of object-related events.

## Active Components

### Core Implementation
- `__init__.py` – Module initialization and public API exports
- `object_manager.py` – Physical object registration, tracking, and management
- `simulation_engine.py` – Physics simulation with forces, constraints, and collisions
- `sensor_integration.py` – IoT sensor data collection and processing
- `analytics.py` – Real-time streaming analytics and predictive modeling

### Documentation
- `README.md` – Module usage and overview
- `API_SPECIFICATION.md` – Complete API documentation
- `USAGE_EXAMPLES.md` – Practical usage demonstrations
- `SECURITY.md` – Security considerations for physical systems

### Examples and Testing
- `examples/` – Usage examples and demonstrations
- `tests/` – Comprehensive test suite
- `docs/` – Additional documentation and guides

## Operating Contracts

### Universal Physical Management Protocols

All physical object management within the Codomyrmex platform must:

1. **Safety First** - Physical operations prioritize safety and prevent hazardous conditions
2. **Real-Time Performance** - Physical simulations and monitoring maintain real-time performance
3. **Resource Awareness** - Physical systems are aware of resource constraints and limitations
4. **Calibration Accuracy** - Sensor data is properly calibrated and drift is detected
5. **Network Resilience** - Physical networks are resilient to connectivity issues

### Module-Specific Guidelines

#### Object Management
- Maintain accurate spatial indexing for efficient queries
- Track object relationships and dependencies
- Provide event-driven notifications for object changes
- Support hierarchical object organization

#### Physics Simulation
- Use appropriate time steps for numerical stability
- Handle constraint violations gracefully
- Provide collision detection and response
- Support multiple physics integration methods

#### Sensor Integration
- Validate sensor data for reasonableness
- Detect and compensate for sensor drift
- Provide sensor health monitoring
- Support sensor calibration procedures

#### Analytics Processing
- Process streaming data efficiently
- Provide configurable alerting thresholds
- Support predictive analytics models
- Maintain data quality and integrity

## Navigation Links

### Module Documentation
- **Module Overview**: [README.md](README.md) - Complete module documentation
- **API Reference**: [API_SPECIFICATION.md](API_SPECIFICATION.md) - Detailed API specification
- **Usage Examples**: [USAGE_EXAMPLES.md](USAGE_EXAMPLES.md) - Practical usage demonstrations

### Related Modules
- **performance**: Performance monitoring for physical simulations
- **logging_monitoring**: Logging of physical object events
- **data_visualization**: Visualization of physical data and analytics
- **security_audit**: Security monitoring for physical systems

### Platform Navigation
- **Parent Directory**: [codomyrmex](../README.md) - Package overview
- **Project Root**: [README](../../../README.md) - Main project documentation

## Agent Coordination

### Integration Points

When integrating with other modules:

1. **Performance Monitoring** - Monitor physics simulation performance
2. **Data Visualization** - Visualize physical object data and analytics
3. **Logging Integration** - Log physical object events and sensor data
4. **Security Integration** - Monitor physical system security
5. **Configuration Management** - Configure physical system parameters

### Quality Gates

Before physical management changes are accepted:

1. **Simulation Accuracy** - Physics simulations produce physically accurate results
2. **Real-Time Performance** - Physical operations meet real-time requirements
3. **Sensor Calibration** - Sensor data is properly calibrated and validated
4. **Safety Compliance** - Physical operations follow safety protocols
5. **Resource Efficiency** - Physical systems use resources efficiently

## Version History

- **v0.1.0** (December 2025) - Initial physical management system with object tracking, physics simulation, sensor integration, and analytics
