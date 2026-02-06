# Agent Guidelines - Embodiment

## Module Overview

Robotics integration with ROS2, sensors, actuators, and 3D coordinate transforms.

## Key Classes

- **ROS2Bridge** — WebSocket bridge to ROS2 nodes
- **Transform3D** — Position, rotation, and scale transforms
- **SensorInterface** — Abstract sensor data handling
- **ActuatorController** — Motor/actuator control

## Agent Instructions

1. **Connect before use** — Call `bridge.connect()` before pub/sub operations
2. **Handle disconnects** — Implement reconnection logic for ROS2 bridge
3. **Transform frame** — Always specify coordinate frame for transforms
4. **Rate limit commands** — Don't flood actuators with commands
5. **Validate sensor data** — Check timestamps and validity flags

## ROS2 Patterns

```python
from codomyrmex.embodiment import ROS2Bridge

bridge = ROS2Bridge(uri="ws://localhost:9090")
await bridge.connect()

# Subscribe to topics
await bridge.subscribe("/camera/image", on_image_callback)
await bridge.subscribe("/odom", on_odometry_callback)

# Publish commands
await bridge.publish("/cmd_vel", {
    "linear": {"x": 0.5, "y": 0, "z": 0},
    "angular": {"x": 0, "y": 0, "z": 0.1}
})
```

## Testing Patterns

```python
# Test transform operations
from codomyrmex.embodiment import Transform3D

t = Transform3D()
t.translate(1, 0, 0)
t.rotate_euler(0, 0, 90)

point = t.apply([0, 1, 0])
assert abs(point[0] - 0) < 0.01  # Rotated 90°
```

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)
