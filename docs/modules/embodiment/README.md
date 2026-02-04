# Embodiment Module Documentation

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The Embodiment module provides physical and robotic system integration capabilities for Codomyrmex. It bridges digital systems with the physical world through sensor and actuator interfaces, ROS2 communication, and 3D spatial transformations. This module enables applications that interact with hardware devices, robotic platforms, and physical environments.

## Key Features

- **ROS2 Bridge**: Communication bridge for integrating with Robot Operating System 2 (ROS2) ecosystems
- **3D Transformations**: Spatial transformation utilities for working with 3D coordinate systems
- **Sensor Integration**: Interfaces for reading and processing data from physical sensors
- **Actuator Control**: Interfaces for commanding and controlling physical actuators
- **Modular Subpackages**: Cleanly separated concerns across ros, sensors, actuators, and transformation submodules

## Key Components

| Component | Description |
|-----------|-------------|
| `ROS2Bridge` | Communication bridge for ROS2 ecosystem integration |
| `Transform3D` | 3D spatial transformation representation and operations |
| `ros` | Submodule for ROS2 communication and bridge functionality |
| `sensors` | Submodule for sensor data acquisition and processing |
| `actuators` | Submodule for actuator command and control interfaces |
| `transformation` | Submodule for spatial coordinate transformations |

## Quick Start

```python
from codomyrmex.embodiment import ROS2Bridge, Transform3D

# Create a ROS2 bridge for robot communication
bridge = ROS2Bridge()

# Work with 3D spatial transformations
transform = Transform3D()
```

## Architecture

The module is organized into four subpackages:

```
embodiment/
  ros/             # ROS2 bridge and communication
  sensors/         # Sensor data interfaces
  actuators/       # Actuator control interfaces
  transformation/  # 3D spatial transformations
```

## Related Modules

- [model_context_protocol](../model_context_protocol/) - Standardized LLM communication interfaces used across modules
- [environment_setup](../environment_setup/) - Environment validation for hardware dependencies

## Navigation

- **Source**: [src/codomyrmex/embodiment/](../../../src/codomyrmex/embodiment/)
- **API Specification**: [src/codomyrmex/embodiment/API_SPECIFICATION.md](../../../src/codomyrmex/embodiment/API_SPECIFICATION.md)
- **Parent**: [docs/modules/](../README.md)
