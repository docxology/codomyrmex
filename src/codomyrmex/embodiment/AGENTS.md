# Agent Guidelines - Embodiment

**Version**: v1.2.0 | **Status**: Active | **Last Updated**: March 2026

## Module Overview

Robotics integration with ROS2, sensors, actuators, and 3D coordinate transforms. Provides an in-process pub/sub message bridge (`ROS2Bridge`) that mirrors ROS2 topic semantics without requiring rclpy, making it suitable for both simulation and real hardware. The `Transform3D` class handles rigid-body transformations using ZYX Euler angles with composition, inverse, and point/vector transformation. Abstract sensor and actuator interfaces define the contract for hardware integration, with `MockSensor` and `MockActuator` available for testing without physical devices.

## Key Files

| File | Purpose |
|------|---------|
| `__init__.py` | Exports `ROS2Bridge`, `Transform3D`, `Vec3` |
| `ros/ros_bridge.py` | `ROS2Bridge` in-process pub/sub bridge with `Message`, `TopicInfo`, topic management, publish, subscribe, history, and latching |
| `transformation/transformation.py` | `Transform3D` rigid-body transform (ZYX Euler) with `compose()`, `inverse()`, `transform_point()`, `transform_vector()`, factory methods |
| `transformation/transformation.py` | `Vec3` frozen dataclass for immutable 3D vectors with arithmetic, dot/cross products, normalization |
| `sensors/__init__.py` | Exports `SensorInterface`, `SensorData`, `MockSensor` |
| `sensors/base.py` | `SensorInterface` ABC with `connect()`, `disconnect()`, `read()`; `SensorData` dataclass; `MockSensor` for testing |
| `actuators/__init__.py` | Exports `ActuatorController`, `ActuatorCommand`, `ActuatorStatus`, `MockActuator` |
| `actuators/base.py` | `ActuatorController` ABC with `connect()`, `disconnect()`, `execute()`, `get_status()`; `ActuatorCommand`/`ActuatorStatus` dataclasses; `MockActuator` for testing |

## Key Classes

- **ROS2Bridge** -- In-process ROS2-style pub/sub message bridge. Supports named topics, multiple subscribers, message history, latching, wildcard matching, and introspection. Does not require rclpy.
- **Message** -- Dataclass representing a message on a topic with `topic`, `payload`, `timestamp`, and `sender`.
- **TopicInfo** -- Dataclass with topic metadata: `name`, `message_type`, `latched`, `subscriber_count`, `total_published`.
- **Transform3D** -- 3D rigid-body transformation using ZYX Euler angles. Provides `transform_point()`, `transform_vector()`, `compose()`, `inverse()`, and factory methods `from_translation()`, `from_rotation()`, `from_yaw()`, `identity()`.
- **Vec3** -- Frozen (immutable) 3D vector dataclass with `+`, `-`, `*`, `dot()`, `cross()`, `length()`, `normalized()`.
- **SensorInterface** -- Abstract base class for sensors. Subclasses implement `connect()`, `disconnect()`, `read()`.
- **SensorData** -- Dataclass for sensor readings with `sensor_id`, `timestamp`, `metadata`, `data`.
- **MockSensor** -- Testing sensor that returns configurable `default_value`.
- **ActuatorController** -- Abstract base class for actuators. Subclasses implement `connect()`, `disconnect()`, `execute()`, `get_status()`.
- **ActuatorCommand** -- Dataclass for actuator commands with `actuator_id`, `command_type`, `parameters`.
- **ActuatorStatus** -- Dataclass for actuator status with `actuator_id`, `status`, `feedback`.
- **MockActuator** -- Testing actuator that simulates position/velocity state.

## Agent Instructions

1. **Connect before use** -- Call `await bridge.connect()` before pub/sub operations.
2. **Handle disconnects** -- Implement reconnection logic for ROS2 bridge.
3. **Transform frame** -- Always specify coordinate frame for transforms.
4. **Rate limit commands** -- Do not flood actuators with commands.
5. **Validate sensor data** -- Check timestamps and validity flags.
6. **Use mock classes** -- For tests without physical hardware, use `MockSensor` and `MockActuator`.

## Operating Contracts

- `ROS2Bridge.publish()` and `subscribe()` are async -- they must be awaited.
- `ROS2Bridge.publish()` will log a warning if called while disconnected but does not raise.
- `ROS2Bridge.create_topic()` is idempotent -- calling it on an existing topic updates its settings.
- `ROS2Bridge.subscribe()` returns an unsubscribe callable. Call it to remove the subscription.
- `Vec3` is frozen (`@dataclass(frozen=True)`) -- it is immutable after creation. All arithmetic returns new instances.
- `Transform3D.compose(other)` applies `other` first, then `self`. This follows the standard mathematical convention `self . other`.
- `Transform3D.inverse()` returns a new transform such that `t.compose(t.inverse())` approximates identity.
- **DO NOT** send actuator commands (`ActuatorController.execute()`) without first verifying `is_connected` is True.
- **DO NOT** read from a sensor (`SensorInterface.read()`) while `is_connected` is False -- `MockSensor` will raise `RuntimeError`.
- Coordinate transforms must specify both source and target frames. Using `transform_point()` without knowing which frame the input is in produces meaningless results.
- `simulate_message()` is synchronous and delivers directly to subscribers without storing in history -- use it for testing only.

## Common Patterns

### ROS2 Bridge (Async)

```python
from codomyrmex.embodiment import ROS2Bridge
import asyncio

async def run_robot():
    bridge = ROS2Bridge(node_name="agent_node")
    await bridge.connect(uri="ws://localhost:9090")

    received = []
    unsubscribe = await bridge.subscribe("/odom", received.append)

    await bridge.publish("/cmd_vel", {
        "linear": {"x": 0.5, "y": 0, "z": 0},
        "angular": {"x": 0, "y": 0, "z": 0.1}
    })

    # Clean up
    unsubscribe()
    bridge.disconnect()

asyncio.run(run_robot())
```

### Transform Composition

```python
from codomyrmex.embodiment import Transform3D

# Translate then rotate
t1 = Transform3D.from_translation(1.0, 0.0, 0.0)
t2 = Transform3D.from_yaw(1.5708)  # ~90 degrees
combined = t2.compose(t1)  # translate first, then rotate

point = combined.transform_point((0, 0, 0))
inverse = combined.inverse()
```

### Sensor and Actuator Testing

```python
from codomyrmex.embodiment.sensors import MockSensor
from codomyrmex.embodiment.actuators import MockActuator, ActuatorCommand

sensor = MockSensor("temp-1", default_value=22.5)
sensor.connect()
reading = sensor.read()
assert reading.data["value"] == 22.5

actuator = MockActuator("motor-1")
actuator.connect()
cmd = ActuatorCommand(actuator_id="motor-1", command_type="move", parameters={"target": 90.0})
actuator.execute(cmd)
assert actuator.current_state["position"] == 90.0
```

## PAI Agent Role Access Matrix

| PAI Agent | Access Level | Primary Capabilities | Trust Level |
|-----------|-------------|---------------------|-------------|
| **Engineer** | Full | Direct Python import, class instantiation, full API access | TRUSTED |
| **Architect** | Read + Design | API review, interface design, dependency analysis | OBSERVED |
| **QATester** | Validation | Integration testing via pytest, output validation | OBSERVED |
| **Researcher** | Read-only | Transform calculations, sensor data analysis | SAFE |

### Engineer Agent
**Use Cases**: Interface with robotic/physical systems via ROS2Bridge, configure sensors and actuators during BUILD/EXECUTE phases.

### Architect Agent
**Use Cases**: Design embodiment abstractions, coordinate frame strategy, sensor-actuator topology review.

### QATester Agent
**Use Cases**: Unit and integration test execution, transform accuracy validation, bridge connectivity verification.

### Researcher Agent
**Use Cases**: Analyze sensor data patterns, review coordinate transform mathematics, study ROS2 topic topologies.

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI.md](PAI.md)
