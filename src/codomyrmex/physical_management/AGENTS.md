# Codomyrmex Agents — src/codomyrmex/physical_management

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose

Provides physical object management, simulation, and sensor integration capabilities for physical computing and IoT device management. Enables tracking, simulation, and analysis of physical objects and their interactions.

## Active Components

- `object_manager.py` - Physical object registration and tracking
- `simulation_engine.py` - Physics simulation for object interactions
- `sensor_integration.py` - Sensor and IoT device integration
- `analytics.py` - Streaming and predictive analytics
- `examples/` - Example implementations
- `__init__.py` - Module exports
- `requirements.txt` - Module dependencies

## Key Classes and Functions

### object_manager.py
- **`PhysicalObjectManager`** - Central manager for physical objects
- **`PhysicalObject`** - Represents a tracked physical object
- **`ObjectRegistry`** - Registry of all known objects
- **`ObjectType`** - Enum of object categories
- **`ObjectStatus`** - Enum: ACTIVE, INACTIVE, UNKNOWN
- **`MaterialType`**, **`MaterialProperties`** - Material characteristics
- **`ObjectEvent`**, **`EventType`** - Event tracking
- **`SpatialIndex`** - Spatial indexing for efficient queries

### simulation_engine.py
- **`PhysicsSimulator`** - Runs physics simulations
- **`ForceField`** - Defines force fields (gravity, magnetic, etc.)
- **`Constraint`** - Physical constraints between objects
- **`Vector3D`** - 3D vector math utilities

### sensor_integration.py
- **`SensorManager`** - Manages connected sensors
- **`SensorReading`** - Individual sensor reading data
- **`DeviceInterface`** - Interface to IoT devices
- **`SensorType`** - Enum of sensor types
- **`DeviceStatus`** - Enum: CONNECTED, DISCONNECTED, ERROR

### analytics.py
- **`StreamingAnalytics`** - Real-time data stream analysis
- **`DataStream`**, **`DataPoint`** - Streaming data structures
- **`PredictiveAnalytics`** - Prediction based on historical data
- **`AnalyticsMetric`**, **`AnalyticsWindow`** - Metric tracking

### Utilities
- **`PhysicalConstants`** - Physical constants (gravity, etc.)
- **`UnitConverter`** - Unit conversions
- **`CoordinateSystem`** - Coordinate system transformations

## Operating Contracts

- Objects assigned unique IDs on registration
- Simulation runs at configurable timestep
- Sensor readings timestamped with arrival time
- Analytics windows are configurable (sliding, tumbling)
- Spatial queries use R-tree indexing

## Signposting

- **Dependencies**: May require numpy for physics calculations
- **Parent Directory**: [codomyrmex](../README.md) - Parent module documentation
- **Related Modules**:
  - `spatial/` - Spatial modeling
  - `logging_monitoring/` - Telemetry logging
- **Project Root**: [../../../README.md](../../../README.md) - Main project documentation
