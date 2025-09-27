# Physical Object Management Module

A comprehensive physical object management, simulation, and sensor integration module for the Codomyrmex platform.

## Features

### Core Object Management
- **Physical Object Registry**: Track and manage physical objects with location and properties
- **Distance Calculations**: Calculate distances between objects and points
- **Property Management**: Dynamic property addition and removal for objects
- **Collision Detection**: Identify objects within collision range
- **Object Clustering**: Group nearby objects automatically
- **Pathfinding**: Find paths between objects using nearby waypoints
- **Batch Operations**: Update multiple objects efficiently

### Advanced Physics Simulation
- **Realistic Physics**: Physics simulation with forces, constraints, and motion
- **Energy Calculations**: Kinetic and potential energy tracking
- **Spring Constraints**: Flexible spring connections between objects
- **Force Fields**: Customizable force fields affecting objects
- **Collision Handling**: Elastic collision detection and response
- **Impulse Application**: Apply sudden forces to objects

### Sensor Integration & Management
- **Multi-sensor Support**: Temperature, humidity, pressure, motion, GPS, and more
- **Device Management**: Register and manage physical sensor devices
- **Sensor Calibration**: Linear regression-based sensor calibration
- **Health Monitoring**: Detect sensor anomalies and performance issues
- **Drift Detection**: Identify sensor drift over time periods
- **Real-time Data**: Live sensor readings with timestamp tracking

### Utilities & Analysis
- **Real-time Monitoring**: Live statistics and status tracking
- **Data Export**: JSON export capabilities for analysis
- **Multi-type Support**: Sensors, actuators, devices, vehicles, and structures
- **Center of Mass**: Calculate center of mass for object groups
- **Boundary Box**: Determine bounding boxes for object collections
- **Unit Conversions**: Built-in unit conversion utilities

## Architecture

### Core Components

1. **Object Manager**: Central registry and management of physical objects
2. **Simulation Engine**: Physics simulation with forces and constraints
3. **Sensor Manager**: Device integration and sensor data collection

### Object Types

- **Sensors**: Temperature, humidity, pressure, motion, light, proximity
- **Actuators**: Motors, valves, switches, displays
- **Devices**: IoT devices, smart appliances, industrial equipment
- **Containers**: Storage units, packages, transport containers
- **Vehicles**: Autonomous vehicles, drones, robotic systems
- **Structures**: Buildings, infrastructure, static objects

## Installation

```bash
pip install -r requirements.txt
```

## Quick Start

```python
from codomyrmex.physical_management import PhysicalObjectManager, ObjectType

# Create object manager
manager = PhysicalObjectManager()

# Create a sensor object
sensor = manager.create_object(
    object_id="temp_sensor_001",
    name="Temperature Sensor",
    object_type=ObjectType.SENSOR,
    x=0.0, y=0.0, z=0.0,
    sensor_type="temperature",
    location="office"
)

print(f"Created sensor: {sensor.name}")
print(f"Current location: {sensor.location}")

# Distance calculations
distance = sensor.distance_to_point(5.0, 5.0, 0.0)
print(f"Distance to point: {distance}")

# Find nearby objects
nearby = manager.get_nearby_objects(0.0, 0.0, 0.0, radius=10.0)
print(f"Found {len(nearby)} nearby objects")

# Batch operations
manager.batch_update_status(["temp_sensor_001"], ObjectStatus.MAINTENANCE)
```

## Physics Simulation

```python
from codomyrmex.physical_management import PhysicsSimulator, Vector3D, ForceField

# Create simulator
sim = PhysicsSimulator()

# Add gravity
sim.gravity = Vector3D(0, -9.81, 0)

# Add force field
force_field = ForceField(
    position=Vector3D(0, 0, 0),
    strength=10.0
)
sim.add_force_field(force_field)

# Register objects
sim.register_object("ball", mass=1.0, position=Vector3D(0, 10, 0))
sim.register_object("block", mass=2.0, position=Vector3D(5, 0, 0))

# Add spring constraint between objects
sim.add_spring_constraint("ball", "block", rest_length=3.0, spring_constant=50.0)

# Apply impulse to ball
sim.apply_impulse("ball", Vector3D(10, 0, 0))

# Run simulation
sim.update_physics(delta_time=0.016)  # ~60 FPS

# Get energy statistics
stats = sim.get_simulation_stats()
print(f"Total energy: {stats['total_energy']}")
```

## Sensor Integration

```python
from codomyrmex.physical_management import SensorManager, SensorType, SensorReading, DeviceInterface

# Create sensor manager
sensor_manager = SensorManager()

# Register a device
device = DeviceInterface(
    device_id="temp_device_001",
    device_type="temperature_sensor",
    sensors=[SensorType.TEMPERATURE, SensorType.HUMIDITY]
)
sensor_manager.register_device(device)

# Create temperature readings
for temp in [20.0, 21.0, 22.0, 23.5, 24.0]:
    reading = SensorReading(
        sensor_id="temp_001",
        sensor_type=SensorType.TEMPERATURE,
        value=temp,
        unit="°C"
    )
    sensor_manager.add_reading(reading)

# Calibrate sensor
reference_points = [(20.0, 19.8), (25.0, 24.9), (30.0, 30.2)]
calibration = sensor_manager.calibrate_sensor("temp_001", reference_points, SensorType.TEMPERATURE)

# Check sensor health
health = sensor_manager.get_sensor_health("temp_001")
print(f"Sensor status: {health['status']}")

# Detect drift
drift = sensor_manager.detect_sensor_drift("temp_001")
print(f"Drift status: {drift['status']}")

# Subscribe to readings
def temperature_callback(reading):
    print(f"Temperature: {reading.value} {reading.unit}")

sensor_manager.subscribe_to_sensor(SensorType.TEMPERATURE, temperature_callback)
```

## API Reference

See [API_SPECIFICATION.md](API_SPECIFICATION.md) for complete API documentation.

## Examples

- [Basic Usage](examples/basic_usage.py) - Core functionality examples
- [Physics Simulation](examples/physics_demo.py) - Physics engine demonstration
- [Sensor Integration](examples/sensor_demo.py) - Device and sensor management

## Testing

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_object_manager.py

# Run with coverage
pytest --cov=codomyrmex.physical_management tests/
```

## Requirements

See [requirements.txt](requirements.txt) for dependencies.

## Contributing

1. Follow the standard Codomyrmex module structure
2. Add comprehensive tests for new features
3. Update documentation for API changes
4. Ensure compatibility with existing modules
