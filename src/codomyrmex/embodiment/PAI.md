# Personal AI Infrastructure — Embodiment Module

**Version**: v0.2.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Embodiment module for Codomyrmex. This is an **Extended Layer** module.

## PAI Capabilities

```python
from codomyrmex.embodiment import ROS2Bridge, Transform3D, ros, sensors, actuators
```

## Key Exports

| Export | Type | Purpose |
|--------|------|---------|
| `ROS2Bridge` | Class | Ros2bridge |
| `Transform3D` | Class | Transform3d |
| `ros` | Function/Constant | Ros |
| `sensors` | Function/Constant | Sensors |
| `actuators` | Function/Constant | Actuators |
| `transformation` | Function/Constant | Transformation |

## PAI Algorithm Phase Mapping

| Phase | Embodiment Contribution |
|-------|------------------------------|
| **EXECUTE** | General module operations |

## Architecture Role

**Extended Layer** — Part of the codomyrmex layered architecture.

## Navigation

- **Self**: [PAI.md](PAI.md)
- **Parent**: [../PAI.md](../PAI.md) — Source-level PAI module map
- **Root Bridge**: [../../../PAI.md](../../../PAI.md) — Authoritative PAI system bridge doc
- **Siblings**: [README.md](README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md) | [API_SPECIFICATION.md](API_SPECIFICATION.md)
