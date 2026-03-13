"""Embodiment module for Codomyrmex.

Robotics integration with ROS2, sensors, actuators, and 3D transforms.
"""

# Submodule exports
from .bridge import EmbodimentBridge
from .ros.ros_bridge import ROS2Bridge
from .telemetry import SensorPayload, TelemetryStream
from .transformation.transformation import Transform3D, Vec3

__all__ = [
    "EmbodimentBridge",
    "ROS2Bridge",
    "SensorPayload",
    "TelemetryStream",
    "Transform3D",
    "Vec3",
    "actuators",
    "ros",
    "sensors",
    "transformation",
]

__version__ = "0.2.0"
