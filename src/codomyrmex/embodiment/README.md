# embodiment

Embodied AI and robotics integration module.

## Overview

This module provides the bridge between Codomyrmex's high-level intelligence and physical or simulated robotic embodiments. It includes support for ROS2 (Robot Operating System), sensor data processing, and actuator control.

## Key Features

- **ROS2 Bridge**: Standardized interface for publishing and subscribing to ROS2 topics.
- **Spatial Logic**: `Transform3D` for translation, rotation, and coordinate conversions.
- **Sensor Integration**: Utilities for processing data from LIDAR, cameras, and IMUs.
- **Motion Planning**: Basic primitives for path finding and robotic movement.

## Usage

```python
from codomyrmex.embodiment import ROS2Bridge, CameraSensor

# Initialize ROS2 bridge
bridge = ROS2Bridge(node_name="codomyrmex_brain")

# Subscribe to a camera stream
camera = CameraSensor(topic="/camera/image_raw")
camera.on_data(lambda img: process_image(img))

# Send a movement command
bridge.publish("/cmd_vel", {"linear": {"x": 0.5}, "angular": {"z": 0.0}})
```

## Navigation Links

- [Functional Specification](SPEC.md)
- [Technical Documentation](AGENTS.md)
