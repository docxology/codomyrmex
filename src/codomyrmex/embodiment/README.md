# embodiment

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The embodiment module bridges digital systems with physical robotics hardware through ROS2 integration, sensor/actuator interfaces, and 3D coordinate transformations. It provides a mock-friendly ROS2 bridge for topic-based pub/sub messaging and utilities for spatial transformations including translation and Euler rotation in 3D space.

## Key Exports

- **`ROS2Bridge`** -- Mock-friendly ROS2 communication bridge supporting topic-based publish/subscribe messaging. Provides `publish()`, `subscribe()`, and `simulate_message()` for testing without a live ROS2 environment.
- **`Transform3D`** -- 3D coordinate transformation class handling translation and Euler rotation (roll, pitch, yaw). Includes `transform_point()` for applying transformations and `deg_to_rad()` static utility.
- **`ros`** -- Submodule containing the ROS2 bridge and related ROS integration utilities.
- **`sensors`** -- Submodule providing sensor interface abstractions for reading physical-world data.
- **`actuators`** -- Submodule providing actuator interface abstractions for controlling physical mechanisms.
- **`transformation`** -- Submodule with coordinate transformation utilities for spatial computing.

## Directory Contents

- `__init__.py` - Module entry point; exports core classes and submodules
- `ros/` - ROS2 bridge implementation (`ros_bridge.py`) for pub/sub messaging
- `sensors/` - Sensor interface abstractions
- `actuators/` - Actuator interface abstractions
- `transformation/` - 3D coordinate transformation utilities (`transformation.py`)
- `AGENTS.md` - Agent integration specification
- `API_SPECIFICATION.md` - Programmatic interface documentation
- `SPEC.md` - Module specification
- `PAI.md` - PAI integration notes

## Navigation

- **Full Documentation**: [docs/modules/embodiment/](../../../docs/modules/embodiment/)
- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: ../../../README.md
