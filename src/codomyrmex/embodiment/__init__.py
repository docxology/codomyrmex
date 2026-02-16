"""Embodiment module for Codomyrmex.

.. deprecated::
    The embodiment module is deprecated and will be removed in a future version.
    It has zero intersection with the coding platform mission. Imports will still
    work but the module receives no further development.
"""

import warnings

warnings.warn(
    "The embodiment module is deprecated and will be removed in a future version.",
    DeprecationWarning,
    stacklevel=2,
)

# Submodule exports (kept for backward compatibility)
try:
    from . import actuators, ros, sensors, transformation
    from .ros.ros_bridge import ROS2Bridge
    from .transformation.transformation import Transform3D
except ImportError:
    ROS2Bridge = None
    Transform3D = None
    actuators = None
    ros = None
    sensors = None
    transformation = None

__all__ = [
    "ROS2Bridge",
    "Transform3D",
    "ros",
    "sensors",
    "actuators",
    "transformation",
]

__version__ = "0.1.0"
