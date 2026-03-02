# Agent Guidelines - Embodiment

**Version**: v1.1.0 | **Status**: Active | **Last Updated**: March 2026

## Module Overview

Robotics integration with ROS2, sensors, actuators, and 3D coordinate transforms.

## Key Classes

- **ROS2Bridge** — WebSocket/in-process bridge to ROS2 nodes
- **Transform3D** — Position, rotation, and scale transforms
- **SensorInterface** — Abstract sensor data handling
- **ActuatorController** — Motor/actuator control

## Agent Instructions

1. **Connect before use** — Call `await bridge.connect()` before pub/sub operations.
2. **Handle disconnects** — Implement reconnection logic for ROS2 bridge.
3. **Transform frame** — Always specify coordinate frame for transforms.
4. **Rate limit commands** — Don't flood actuators with commands.
5. **Validate sensor data** — Check timestamps and validity flags.
6. **Use mock classes** — For tests without physical hardware, use `MockSensor` and `MockActuator`.

## ROS2 Patterns (Async)

```python
from codomyrmex.embodiment import ROS2Bridge
import asyncio

async def run_robot():
    bridge = ROS2Bridge(node_name="agent_node")
    await bridge.connect(uri="ws://localhost:9090")

    async def on_image(msg):
        # Process image
        pass

    # Subscribe to topics
    await bridge.subscribe("/camera/image", on_image)
    await bridge.subscribe("/odom", on_odometry_callback)

    # Publish commands
    await bridge.publish("/cmd_vel", {
        "linear": {"x": 0.5, "y": 0, "z": 0},
        "angular": {"x": 0, "y": 0, "z": 0.1}
    })

asyncio.run(run_robot())
```

## Testing Patterns (Zero-Mock)

```python
# Test transform operations
from codomyrmex.embodiment import Transform3D

t = Transform3D.from_translation(1, 0, 0)
t = t.compose(Transform3D.from_rotation(0, 0, 1.5708)) # 90 deg

point = t.apply((0, 1, 0))
assert abs(point[0] - 0) < 0.01  # Rotated 90°
```

## PAI Agent Role Access Matrix

| PAI Agent | Access Level | Primary Capabilities | Trust Level |
|-----------|-------------|---------------------|-------------|
| **Engineer** | Full | Direct Python import, class instantiation, full API access | TRUSTED |
| **Architect** | Read + Design | API review, interface design, dependency analysis | OBSERVED |
| **QATester** | Validation | Integration testing via pytest, output validation | OBSERVED |

### Engineer Agent
**Use Cases**: Interface with robotic/physical systems via ROS2Bridge, configure sensors and actuators during BUILD/EXECUTE phases

### Architect Agent
**Use Cases**: Design embodiment abstractions, coordinate frame strategy, sensor-actuator topology review

### QATester Agent
**Use Cases**: Unit and integration test execution, transform accuracy validation, bridge connectivity verification

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI.md](PAI.md)
