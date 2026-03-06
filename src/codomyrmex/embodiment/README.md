# Embodiment Module

**Version**: v1.1.4 | **Status**: Active | **Last Updated**: March 2026

Robotics integration with ROS2, sensors, actuators, and 3D transforms.

## Features

- **ROS2Bridge**: In-process pub/sub system mirroring ROS2 semantics.
- **Transform3D**: 3D rigid-body transformations (translation + ZYX Euler rotation).
- **Sensors**: Base classes for sensor integration with mock implementations.
- **Actuators**: Base classes for motor/actuator control with mock implementations.

## PAI Integration

| Algorithm Phase | Role | Tools Used |
|----------------|------|-----------|
| **EXECUTE** | Control robotic and physical systems via ROS2 bridge | Direct Python import |
| **OBSERVE** | Collect sensor data from cameras, lidar, and actuators | Direct Python import |
| **BUILD** | Configure embodiment parameters and 3D transforms | Direct Python import |

## Installation

```bash
uv add codomyrmex
```

## Quick Start

### ROS2 Integration

```python
from codomyrmex.embodiment import ROS2Bridge
import asyncio

async def main():
    bridge = ROS2Bridge(node_name="my_robot")
    await bridge.connect(uri="localhost:9090")

    async def on_image(msg):
        print(f"Received image: {msg.payload}")

    await bridge.subscribe("/camera/image", on_image)
    await bridge.publish("/cmd_vel", {"linear": 0.5, "angular": 0.1})

asyncio.run(main())
```

### 3D Transforms

```python
from codomyrmex.embodiment import Transform3D

# Create transform
transform = Transform3D()
transform = Transform3D.from_translation(1.0, 0.0, 0.5)
transform = transform.compose(Transform3D.from_rotation(0, 0, 0.785)) # 45 degrees

# Apply to point
world_point = transform.apply((0, 0, 0))
print(f"World point: {world_point}")
```

### Sensors and Actuators

```python
from codomyrmex.embodiment.sensors import MockSensor
from codomyrmex.embodiment.actuators import MockActuator, ActuatorCommand

# Sensor usage
sensor = MockSensor("temp_1", default_value=25.0)
sensor.connect()
data = sensor.read()
print(f"Sensor data: {data.data}")

# Actuator usage
actuator = MockActuator("motor_1")
actuator.connect()
cmd = ActuatorCommand("motor_1", "move", {"target": 10.0})
actuator.execute(cmd)
status = actuator.get_status()
print(f"Actuator status: {status.feedback}")
```

## Submodules

| Module | Description |
|--------|-------------|
| `ros` | ROS2 bridge and message handling |
| `sensors` | Sensor data processing |
| `actuators` | Motor and actuator control |
| `transformation` | 3D coordinate transforms |

## Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k embodiment -v
```

## Documentation

- [Module Documentation](../../../docs/modules/embodiment/README.md)
- [Agent Guide](../../../docs/modules/embodiment/AGENTS.md)
- [Specification](../../../docs/modules/embodiment/SPEC.md)

## Navigation

- [SPEC](SPEC.md) | [AGENTS](AGENTS.md) | [PAI.md](PAI.md)
