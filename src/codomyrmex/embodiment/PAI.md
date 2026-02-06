# Personal AI Infrastructure — Embodiment Module

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The Embodiment module provides PAI integration for physical agent embodiment.

## PAI Capabilities

### Robot Control

Control physical robots:

```python
from codomyrmex.embodiment import RobotController

robot = RobotController()
robot.move_to(x=10, y=20)
robot.pick_object("cube_1")
```

### Sensor Integration

Read sensor data:

```python
from codomyrmex.embodiment import SensorArray

sensors = SensorArray()
distance = sensors.read("proximity")
temperature = sensors.read("thermal")
```

## PAI Integration Points

| Component | PAI Use Case |
|-----------|-------------|
| `RobotController` | Control robots |
| `SensorArray` | Read sensors |
| `Actuator` | Control actuators |

## Navigation

- [README](README.md) | [AGENTS](AGENTS.md) | [SPEC](SPEC.md)
