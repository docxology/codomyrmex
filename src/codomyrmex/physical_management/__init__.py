"""Physical Object Management Module for Codomyrmex.

This module provides physical object management, simulation,
and sensor integration capabilities for the Codomyrmex platform, enabling
physical computing and IoT device management.
"""

from .analytics import (
    AnalyticsMetric,
    AnalyticsWindow,
    DataPoint,
    DataStream,
    PredictiveAnalytics,
    StreamingAnalytics,
    StreamingMode,
)
from .object_manager import (
    EventType,
    MaterialProperties,
    MaterialType,
    ObjectEvent,
    ObjectRegistry,
    ObjectStatus,
    ObjectType,
    PhysicalObject,
    PhysicalObjectManager,
    SpatialIndex,
)
from .sensor_integration import (
    CoordinateSystem,
    DeviceInterface,
    DeviceStatus,
    PhysicalConstants,
    SensorManager,
    SensorReading,
    SensorType,
    UnitConverter,
)
from .simulation_engine import Constraint, ForceField, PhysicsSimulator, Vector3D

__version__ = "0.2.0"
__all__ = [
    # Physical Object Management
    "PhysicalObjectManager",
    "PhysicalObject",
    "ObjectRegistry",
    "ObjectType",
    "ObjectStatus",
    "MaterialType",
    "EventType",
    "MaterialProperties",
    "ObjectEvent",
    "SpatialIndex",
    # Simulation Engine
    "PhysicsSimulator",
    "ForceField",
    "Constraint",
    "Vector3D",
    # Sensor Integration
    "SensorManager",
    "SensorReading",
    "DeviceInterface",
    "SensorType",
    "DeviceStatus",
    # Analytics
    "StreamingAnalytics",
    "DataStream",
    "PredictiveAnalytics",
    "AnalyticsMetric",
    "StreamingMode",
    "DataPoint",
    "AnalyticsWindow",
    # Utilities
    "PhysicalConstants",
    "UnitConverter",
    "CoordinateSystem",
]
