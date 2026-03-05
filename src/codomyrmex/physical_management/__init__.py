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
    "AnalyticsMetric",
    "AnalyticsWindow",
    "Constraint",
    "CoordinateSystem",
    "DataPoint",
    "DataStream",
    "DeviceInterface",
    "DeviceStatus",
    "EventType",
    "ForceField",
    "MaterialProperties",
    "MaterialType",
    "ObjectEvent",
    "ObjectRegistry",
    "ObjectStatus",
    "ObjectType",
    # Utilities
    "PhysicalConstants",
    "PhysicalObject",
    # Physical Object Management
    "PhysicalObjectManager",
    # Simulation Engine
    "PhysicsSimulator",
    "PredictiveAnalytics",
    # Sensor Integration
    "SensorManager",
    "SensorReading",
    "SensorType",
    "SpatialIndex",
    # Analytics
    "StreamingAnalytics",
    "StreamingMode",
    "UnitConverter",
    "Vector3D",
]
