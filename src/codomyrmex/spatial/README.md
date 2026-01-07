# spatial

## Signposting
- **Parent**: [codomyrmex](../README.md)
- **Children**:
    - [four_d](four_d/README.md)
    - [three_d](three_d/README.md)
    - [world_models](world_models/README.md)
- **Key Artifacts**:
    - [Agent Guide](AGENTS.md)
    - [Functional Spec](SPEC.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Overview

3D/4D visualization, modeling, and world model capabilities for spatial computing. Provides scene creation and manipulation, mesh generation, camera and lighting control, image rendering, time-series spatial data, animation sequences, temporal interpolation, environment representation, physics simulation, and agent-environment interaction. Supports AR/VR/XR capabilities with pluggable rendering backends.

## Directory Contents
- `README.md` – File
- `SPEC.md` – File
- `__init__.py` – File
- `four_d/` – Subdirectory
- `three_d/` – Subdirectory
- `world_models/` – Subdirectory

## Navigation
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: [README](../../../README.md)

## Getting Started

To use this module in your project, import the necessary components:

```python
from codomyrmex.spatial.three_d import Scene3D, Object3D, Camera3D
from codomyrmex.spatial.four_d import QuadrayCoordinate
from codomyrmex.spatial.world_models import WorldModel

# Create a 3D scene
scene = Scene3D()
obj = Object3D(position=(0, 0, 0), mesh="cube")
scene.add_object(obj)
camera = Camera3D(position=(5, 5, 5), target=(0, 0, 0))
image = scene.render(camera)

# Work with 4D coordinates
coord = QuadrayCoordinate(a=1, b=2, c=3, d=4)
print(f"4D coordinate: {coord}")

# Create a world model
world = WorldModel()
world.add_environment(env_id="test_env", properties={...})
```

