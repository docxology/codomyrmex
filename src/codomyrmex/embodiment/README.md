# Embodiment Module

**Version**: v0.1.0 | **Status**: Active

Robotics integration with ROS2, sensors, actuators, and 3D transforms.


## Installation

```bash
uv uv add codomyrmex
```

Or for development:

```bash
uv sync
```

## Key Exports

### Submodules
- **`actuators/`** — Actuator control submodule.
- **`ros/`** — ROS integration submodule.
- **`sensors/`** — Sensor interfaces submodule.
- **`transformation/`** — Transformations submodule.

## Quick Start

```python
from codomyrmex.embodiment import ROS2Bridge, Transform3D

# ROS2 integration
bridge = ROS2Bridge()
bridge.connect(uri="localhost:9090")

# Subscribe to sensor data
bridge.subscribe("/camera/image", on_image)
bridge.subscribe("/lidar/scan", on_scan)

# Publish commands
bridge.publish("/cmd_vel", {"linear": 0.5, "angular": 0.1})

# 3D transforms
transform = Transform3D()
transform.translate(1.0, 0.0, 0.5)
transform.rotate_euler(roll=0, pitch=0, yaw=45)

# Apply to point
world_point = transform.apply([0, 0, 0])
```

## Submodules

| Module | Description |
|--------|-------------|
| `ros` | ROS2 bridge and message handling |
| `sensors` | Sensor data processing |
| `actuators` | Motor and actuator control |
| `transformation` | 3D coordinate transforms |

## Exports

| Class | Description |
|-------|-------------|
| `ROS2Bridge` | WebSocket bridge to ROS2 |
| `Transform3D` | 3D position and rotation transform |


## Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k embodiment -v
```


## Documentation

- [Module Documentation](../../../docs/modules/embodiment/README.md)
- [Agent Guide](../../../docs/modules/embodiment/AGENTS.md)
- [Specification](../../../docs/modules/embodiment/SPEC.md)

## Navigation

- [SPEC](SPEC.md) | [AGENTS](AGENTS.md) | [PAI](PAI.md)
