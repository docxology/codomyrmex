# physical_management

**Version**: v0.2.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Physical object management, simulation, and sensor integration module for the Codomyrmex platform. Enables physical computing and IoT device management through an object registry with spatial indexing, a physics simulator with force fields and constraints, a sensor manager supporting multiple device types, and a streaming analytics engine with predictive capabilities.

## Key Exports

### Physical Object Management
- **`PhysicalObjectManager`** -- Central manager for creating, updating, and querying physical objects in the registry
- **`PhysicalObject`** -- Represents a physical entity with position, material properties, and lifecycle events
- **`ObjectRegistry`** -- Storage and retrieval system for physical objects with lookup by ID, type, and status
- **`ObjectType`** -- Enum defining categories of physical objects
- **`ObjectStatus`** -- Enum for object lifecycle states (active, inactive, maintenance, etc.)
- **`MaterialType`** -- Enum for material classifications used in physics simulation
- **`EventType`** -- Enum for physical object events (created, moved, collision, etc.)
- **`MaterialProperties`** -- Dataclass holding physical material attributes (density, friction, elasticity)
- **`ObjectEvent`** -- Records an event that occurred on a physical object with timestamp and metadata
- **`SpatialIndex`** -- Spatial data structure for efficient proximity queries and range searches

### Simulation Engine
- **`PhysicsSimulator`** -- Runs physics simulations with configurable timestep, applying forces and constraints
- **`ForceField`** -- Defines a spatial force (gravity, magnetic, custom) that acts on objects
- **`Constraint`** -- Defines physical constraints between objects (distance, hinge, fixed)
- **`Vector3D`** -- 3D vector type used for positions, velocities, and forces

### Sensor Integration
- **`SensorManager`** -- Manages sensor devices, handles readings, and routes data to consumers
- **`SensorReading`** -- Timestamped data point from a sensor with value, unit, and quality metadata
- **`DeviceInterface`** -- Abstract interface for communicating with physical sensor/actuator hardware
- **`SensorType`** -- Enum for sensor categories (temperature, pressure, accelerometer, etc.)
- **`DeviceStatus`** -- Enum for device operational states (online, offline, error, calibrating)

### Analytics
- **`StreamingAnalytics`** -- Real-time analytics pipeline that processes data streams with windowed aggregation
- **`DataStream`** -- Represents a continuous stream of data points from one or more sources
- **`PredictiveAnalytics`** -- Applies predictive models to sensor and object data for forecasting
- **`AnalyticsMetric`** -- Defines a computed metric derived from streaming data
- **`StreamingMode`** -- Enum for streaming processing modes (batch, micro-batch, continuous)
- **`DataPoint`** -- Single data observation with timestamp, value, and source metadata
- **`AnalyticsWindow`** -- Defines a time or count window for aggregation operations

### Utilities
- **`PhysicalConstants`** -- Standard physical constants (gravity, speed of light, etc.)
- **`UnitConverter`** -- Converts between measurement units (metric, imperial, SI)
- **`CoordinateSystem`** -- Defines and transforms between coordinate systems

## Directory Contents

- `object_manager.py` -- PhysicalObjectManager, PhysicalObject, ObjectRegistry, and spatial indexing
- `simulation_engine.py` -- PhysicsSimulator, ForceField, Constraint, and Vector3D
- `sensor_integration.py` -- SensorManager, DeviceInterface, readings, and device types
- `analytics.py` -- StreamingAnalytics, PredictiveAnalytics, DataStream, and windowing
- `examples/` -- Usage examples and demo scripts

## Quick Start

```python
from codomyrmex.physical_management import AnalyticsMetric, StreamingMode

# Create a AnalyticsMetric instance
analyticsmetric = AnalyticsMetric()

# Use StreamingMode for additional functionality
streamingmode = StreamingMode()
```


## Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k physical_management -v
```

## Navigation

- **Full Documentation**: [docs/modules/physical_management/](../../../docs/modules/physical_management/)
- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: ../../../README.md
