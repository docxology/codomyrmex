"""Physical Object Management Module for Codomyrmex.

This module provides physical object management, simulation,
and sensor integration capabilities for the Codomyrmex platform, enabling
physical computing and IoT device management.
"""

from .analytics import *
from .object_manager import *
from .sensor_integration import *
from .simulation_engine import *

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
