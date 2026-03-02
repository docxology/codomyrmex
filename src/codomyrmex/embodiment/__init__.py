"""Embodiment module for Codomyrmex.

Robotics integration with ROS2, sensors, actuators, and 3D transforms.
"""

# Submodule exports
from .ros.ros_bridge import ROS2Bridge
from .transformation.transformation import Transform3D, Vec3

__all__ = [
    "ROS2Bridge",
    "Transform3D",
    "Vec3",
    "ros",
    "sensors",
    "actuators",
    "transformation",
]

__version__ = "0.2.0"
