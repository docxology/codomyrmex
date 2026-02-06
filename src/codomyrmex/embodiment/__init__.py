"""Embodiment module for Codomyrmex."""

# Submodule exports
from . import actuators, ros, sensors, transformation
from .ros.ros_bridge import ROS2Bridge
from .transformation.transformation import Transform3D

__all__ = [
    "ROS2Bridge",
    "Transform3D",
    "ros",
    "sensors",
    "actuators",
    "transformation",
]

__version__ = "0.1.0"

