# Physical Gen -- Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

The physical_gen subpackage provides 10 generator functions split across domain-specific files, each returning complete Python module source or Markdown documentation for the physical management module scaffolding.

## Architecture

Single-responsibility file layout: one generator function per file, all aggregated by `__init__.py`. The generated code defines three subsystems:

1. **Object Management**: `PhysicalObject`, `ObjectRegistry` (grid-indexed), `PhysicalObjectManager`
2. **Physics Simulation**: `Vector3D`, `ForceField`, `Constraint`, `PhysicsSimulator` (Verlet integration)
3. **Sensor Integration**: `SensorType`, `SensorReading`, `DeviceInterface`, `SensorManager` (pub/sub, bounded buffer)

## Key Functions

### `generate_physical_manager_content` (manager.py)

Produces source for the object management layer:

| Generated Class | Key Methods | Notes |
|----------------|-------------|-------|
| `ObjectType` (Enum) | -- | SENSOR, ACTUATOR, DEVICE, CONTAINER, VEHICLE, STRUCTURE |
| `ObjectStatus` (Enum) | -- | ACTIVE, INACTIVE, MAINTENANCE, ERROR, OFFLINE |
| `PhysicalObject` | `update_location`, `update_status`, `to_dict` | Dataclass with 3D coordinates |
| `ObjectRegistry` | `register_object`, `get_object`, `get_objects_by_type`, `get_objects_in_area`, `save_to_file`, `load_from_file` | Grid-based spatial index for proximity queries |
| `PhysicalObjectManager` | `create_object`, `update_object_location`, `get_nearby_objects`, `get_statistics` | High-level facade over ObjectRegistry |

### `generate_physical_simulation_content` (simulation.py)

Produces source for the physics engine:

| Generated Class | Key Methods | Notes |
|----------------|-------------|-------|
| `Vector3D` | `__add__`, `__sub__`, `__mul__`, `magnitude`, `normalize` | Arithmetic dataclass |
| `ForceField` | `calculate_force` | Inverse-square falloff |
| `Constraint` | -- | Distance constraint between two object IDs |
| `PhysicsSimulator` | `register_object`, `add_force_field`, `add_constraint`, `update_physics`, `get_object_state`, `get_simulation_stats` | Gravity + force fields + Verlet integration |

### `generate_sensor_integration_content` (sensor.py)

Produces source for sensor and device management:

| Generated Class | Key Methods | Notes |
|----------------|-------------|-------|
| `SensorType` (Enum) | -- | 10 types: TEMPERATURE through MAGNETOMETER |
| `DeviceStatus` (Enum) | -- | CONNECTED, DISCONNECTED, ERROR, UNKNOWN |
| `SensorReading` | `to_dict` | Dataclass with sensor_id, type, value, unit, timestamp |
| `DeviceInterface` | -- | Dataclass for connected devices |
| `SensorManager` | `register_device`, `add_reading`, `get_latest_reading`, `subscribe_to_sensor`, `export_readings`, `get_statistics` | Pub/sub callbacks, bounded to 10k readings |
| `UnitConverter` | `celsius_to_fahrenheit`, `meters_to_feet`, `pascals_to_psi` | Static conversion methods |
| `CoordinateSystem` | `cartesian_to_spherical`, `spherical_to_cartesian` | Static coordinate transforms |

## Dependencies

- **Internal**: None (generators return string literals with no runtime imports)
- **External**: Standard library only

## Constraints

- All returned strings must be syntactically valid Python 3.10+ or valid Markdown.
- The `ObjectRegistry` spatial index uses integer grid keys (`int(x), int(y), int(z)`); fractional coordinates are truncated.
- `SensorManager` caps stored readings at `max_readings` (10,000) using tail truncation.
- Zero-mock: real data only, `NotImplementedError` for unimplemented paths.

## Error Handling

- Generated code logs via module-level `logger = get_logger(__name__)`.
- `ObjectRegistry.unregister_object` returns `None` for unknown IDs (no exception).
- `SensorManager` callback errors are caught and logged, not propagated.
- All errors logged before propagation.
