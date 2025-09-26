"""Physical Object Management Module for Codomyrmex.

This module provides comprehensive physical object management, simulation,
and sensor integration capabilities for the Codomyrmex platform, enabling
advanced physical computing and IoT device management.
"""

from .object_manager import *
from .simulation_engine import *
from .sensor_integration import *

__version__ = "0.1.0"
__all__ = [
    # Physical Object Management
    "PhysicalObjectManager", "PhysicalObject", "ObjectRegistry",

    # Simulation Engine
    "PhysicsSimulator", "ForceField", "Constraint",

    # Sensor Integration
    "SensorManager", "SensorReading", "DeviceInterface",

    # Utilities
    "PhysicalConstants", "UnitConverter", "CoordinateSystem"
]
