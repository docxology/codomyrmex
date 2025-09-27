# Physical Management API Reference

## Overview

The Physical Management module provides comprehensive APIs for managing physical objects, physics simulation, sensor integration, and real-time analytics. This reference covers all classes, methods, and their usage patterns.

## Core Classes

### PhysicalObject

Represents a physical object in the system with location, properties, and material characteristics.

```python
@dataclass
class PhysicalObject:
    id: str                                    # Unique identifier
    name: str                                  # Human-readable name
    object_type: ObjectType                    # Type of object
    location: Tuple[float, float, float]       # 3D coordinates (x, y, z)
    properties: Dict[str, Any]                 # Custom properties
    status: ObjectStatus                       # Current status
    material: MaterialType                     # Material type
    mass: float                               # Mass in kg
    volume: float                             # Volume in m³
    temperature: float                        # Temperature in Kelvin
    connections: Set[str]                     # Connected object IDs
    tags: Set[str]                           # Object tags
```

#### Key Methods

- `distance_to(other_object: PhysicalObject) -> float`: Calculate distance to another object
- `distance_to_point(x: float, y: float, z: float) -> float`: Calculate distance to a point
- `is_within_range(x: float, y: float, z: float, max_distance: float) -> bool`: Check if within range
- `add_property(key: str, value: Any) -> None`: Add/update property
- `remove_property(key: str) -> Optional[Any]`: Remove property
- `add_tag(tag: str) -> None`: Add tag
- `remove_tag(tag: str) -> bool`: Remove tag
- `connect_to(other_object_id: str) -> None`: Connect to another object
- `disconnect_from(other_object_id: str) -> bool`: Disconnect from object
- `update_temperature(new_temperature: float) -> None`: Update temperature
- `calculate_thermal_energy() -> float`: Calculate thermal energy

### PhysicalObjectManager

Main manager for physical object operations with advanced spatial and network analysis.

#### Object Management

```python
def create_object(object_id: str, name: str, object_type: ObjectType,
                 x: float, y: float, z: float, 
                 material: MaterialType = MaterialType.UNKNOWN,
                 mass: float = 1.0, volume: float = 1.0, 
                 temperature: float = 293.15, **properties) -> PhysicalObject
```

#### Spatial Analysis

- `get_nearby_objects(x: float, y: float, z: float, radius: float) -> List[PhysicalObject]`
- `calculate_center_of_mass(object_ids: Optional[List[str]] = None) -> Tuple[float, float, float]`
- `get_boundary_box(object_ids: Optional[List[str]] = None) -> Dict[str, Tuple[float, float]]`
- `detect_object_clusters(cluster_radius: float = 3.0, min_cluster_size: int = 2) -> List[List[PhysicalObject]]`

#### Collision and Pathfinding

- `find_path_between_objects(start_object_id: str, end_object_id: str, max_steps: int = 10) -> Optional[List[PhysicalObject]]`

#### Batch Operations

- `batch_update_status(object_ids: List[str], new_status: ObjectStatus) -> int`
- `batch_move_objects(moves: Dict[str, Tuple[float, float, float]]) -> int`

### ObjectRegistry

Registry for managing physical objects with event system and network analysis.

#### Event System

```python
def add_event_handler(event_type: EventType, handler: Callable[[ObjectEvent], None]) -> None
def remove_event_handler(event_type: EventType, handler: Callable[[ObjectEvent], None]) -> bool
def get_events(event_type: Optional[EventType] = None, 
               object_id: Optional[str] = None,
               since: Optional[float] = None) -> List[ObjectEvent]
```

#### Network Analysis

- `get_network_topology() -> Dict[str, List[str]]`: Get connection topology
- `find_path_through_network(start_id: str, end_id: str, max_hops: int = 10) -> Optional[List[str]]`: Find network path
- `analyze_network_metrics() -> Dict[str, Any]`: Analyze network metrics (degree, clustering, density)

#### Tag-based Queries

- `get_objects_by_tags(tags: Set[str], match_all: bool = True) -> List[PhysicalObject]`: Find objects by tags

#### Advanced Queries

- `get_objects_by_status(status: ObjectStatus) -> List[PhysicalObject]`
- `get_objects_by_property(property_key: str, property_value: Any) -> List[PhysicalObject]`
- `find_nearest_object(x: float, y: float, z: float, object_type: Optional[ObjectType] = None) -> Optional[PhysicalObject]`
- `check_collisions(collision_distance: float = 1.0) -> List[Tuple[PhysicalObject, PhysicalObject]]`

## Physics Simulation

### PhysicsSimulator

Advanced physics simulation with energy tracking and constraints.

#### Energy Calculations

- `calculate_kinetic_energy(object_id: str) -> float`: Calculate KE for object
- `calculate_potential_energy(object_id: str) -> float`: Calculate PE for object
- `calculate_total_kinetic_energy() -> float`: Total system KE
- `calculate_total_potential_energy() -> float`: Total system PE

#### Force and Motion

- `apply_impulse(object_id: str, impulse: Vector3D) -> bool`: Apply sudden force
- `set_object_velocity(object_id: str, velocity: Vector3D) -> bool`: Set velocity
- `add_spring_constraint(object1_id: str, object2_id: str, rest_length: float, spring_constant: float, damping: float = 0.1) -> bool`

#### Collision Handling

- `detect_collisions(collision_radius: float = 0.5) -> List[Tuple[str, str]]`: Detect collisions
- `handle_elastic_collision(obj1_id: str, obj2_id: str) -> bool`: Handle elastic collision

### Vector3D

3D vector operations for physics calculations.

```python
# Basic operations
vec1 + vec2          # Addition
vec1 - vec2          # Subtraction  
vec * scalar         # Scaling
vec.magnitude()      # Calculate magnitude
vec.normalize()      # Normalize to unit vector
```

## Sensor Integration

### SensorManager

Advanced sensor management with calibration, health monitoring, and drift detection.

#### Calibration

```python
def calibrate_sensor(sensor_id: str, reference_values: List[Tuple[float, float]], 
                    sensor_type: SensorType) -> Dict[str, float]
def apply_calibration(reading: SensorReading) -> SensorReading
```

#### Health Monitoring

```python
def get_sensor_health(sensor_id: str, time_window: float = 3600) -> Dict[str, Any]
def detect_sensor_drift(sensor_id: str, baseline_period: float = 86400,
                       comparison_period: float = 3600) -> Dict[str, Any]
```

#### Data Management

- `add_reading(reading: SensorReading) -> None`: Add sensor reading
- `get_latest_reading(sensor_type: SensorType) -> Optional[SensorReading]`: Get latest reading
- `get_readings_by_type(sensor_type: SensorType, start_time: Optional[float] = None, end_time: Optional[float] = None) -> List[SensorReading]`
- `export_readings(file_path: str, sensor_type: Optional[SensorType] = None) -> None`: Export data

## Real-time Analytics

### StreamingAnalytics

Central analytics manager for real-time data processing.

#### Stream Management

```python
def create_stream(stream_id: str, buffer_size: int = 10000,
                 window_duration: float = 60.0) -> DataStream
def get_stream(stream_id: str) -> Optional[DataStream]
def add_data(stream_id: str, value: float, source_id: str,
            metadata: Optional[Dict[str, Any]] = None) -> bool
```

#### Alert System

```python
def create_alert(stream_id: str, condition: str, 
                threshold: float, message: str) -> None
```

Supported conditions:
- `"above"`: Trigger when value > threshold
- `"below"`: Trigger when value < threshold
- `"equal"`: Trigger when value ≈ threshold

### DataStream

Individual data stream with windowed analytics.

#### Methods

- `add_data_point(value: float, source_id: str, metadata: Optional[Dict[str, Any]] = None) -> None`
- `subscribe(callback: Callable[[DataPoint], None]) -> None`: Subscribe to updates
- `get_recent_data(duration: float) -> List[DataPoint]`: Get recent data
- `get_current_metrics() -> Dict[AnalyticsMetric, float]`: Get current window metrics
- `get_stream_statistics() -> Dict[str, Any]`: Get stream statistics

### PredictiveAnalytics

Machine learning and statistical prediction methods.

#### Prediction Methods

```python
def predict_linear_trend(data_points: List[DataPoint], 
                        future_seconds: float) -> Optional[float]
def detect_anomalies(data_points: List[DataPoint],
                    std_dev_threshold: float = 3.0) -> List[DataPoint]
def calculate_correlation(stream1_data: List[DataPoint],
                         stream2_data: List[DataPoint]) -> Optional[float]
```

## Enums and Constants

### ObjectType
- `SENSOR`, `ACTUATOR`, `DEVICE`, `CONTAINER`, `VEHICLE`, `STRUCTURE`

### ObjectStatus
- `ACTIVE`, `INACTIVE`, `MAINTENANCE`, `ERROR`, `OFFLINE`, `INITIALIZING`, `SHUTTING_DOWN`, `CALIBRATING`

### MaterialType
- `METAL`, `PLASTIC`, `WOOD`, `GLASS`, `CERAMIC`, `COMPOSITE`, `LIQUID`, `GAS`, `UNKNOWN`

### EventType
- `CREATED`, `MOVED`, `STATUS_CHANGED`, `PROPERTY_UPDATED`, `COLLISION`, `DESTROYED`, `CONNECTED`, `DISCONNECTED`

### SensorType
- `TEMPERATURE`, `HUMIDITY`, `PRESSURE`, `MOTION`, `LIGHT`, `PROXIMITY`, `GPS`, `ACCELEROMETER`, `GYROSCOPE`, `MAGNETOMETER`

### AnalyticsMetric
- `MEAN`, `MEDIAN`, `STD_DEV`, `MIN`, `MAX`, `COUNT`, `RATE`, `PERCENTILE_95`, `PERCENTILE_99`

## Material Properties

### MaterialProperties

Physical properties for realistic simulations.

```python
@dataclass
class MaterialProperties:
    density: float              # kg/m³
    elasticity: float          # Young's modulus in Pa
    thermal_conductivity: float # W/(m⋅K)
    specific_heat: float       # J/(kg⋅K)
    melting_point: float       # K
    friction_coefficient: float = 0.5
    restitution: float = 0.5   # Coefficient of restitution
```

Create from material type:
```python
props = MaterialProperties.from_material_type(MaterialType.METAL)
```

## Error Handling

All methods include proper error handling and logging. Common exceptions:

- `ValueError`: Invalid parameters or data
- `AttributeError`: Missing required attributes  
- `KeyError`: Object or resource not found
- Custom logging through Python logging module

## Performance Considerations

### Spatial Indexing
- Objects are automatically indexed in spatial grid for O(1) spatial queries
- Grid size configurable in ObjectRegistry constructor
- Efficient for large numbers of objects

### Memory Management
- Event history limited to 10,000 events by default
- Data streams have configurable buffer sizes
- Weak references used where appropriate to prevent memory leaks

### Thread Safety
- Core operations are thread-safe using RLock
- Event handlers called asynchronously
- Analytics streams support concurrent access

## Usage Patterns

### Basic Object Management
```python
manager = PhysicalObjectManager()
sensor = manager.create_object("sensor_001", "Temperature Sensor", 
                              ObjectType.SENSOR, x=0, y=0, z=0,
                              material=MaterialType.PLASTIC)
sensor.add_tag("critical")
nearby = manager.get_nearby_objects(0, 0, 0, radius=10)
```

### Physics Simulation
```python
sim = PhysicsSimulator()
sim.register_object("ball", mass=1.0, position=Vector3D(0, 10, 0))
sim.add_spring_constraint("ball", "anchor", rest_length=5.0, spring_constant=100.0)
sim.update_physics(0.016)  # 60 FPS
energy = sim.calculate_total_kinetic_energy()
```

### Real-time Analytics
```python
analytics = StreamingAnalytics()
stream = analytics.create_stream("temperature", window_duration=60.0)
analytics.add_data("temperature", 25.5, "sensor_001")
metrics = stream.get_current_metrics()
```

### Event Handling
```python
def on_object_created(event):
    print(f"Created: {event.object_id}")

manager.registry.add_event_handler(EventType.CREATED, on_object_created)
```

## Version History

- **v0.2.0**: Added advanced features (materials, events, analytics, networking)
- **v0.1.0**: Initial release with basic object management and physics

---

For more examples, see the `examples/` directory and the comprehensive test suite in `tests/`.
