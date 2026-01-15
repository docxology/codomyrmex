# Spatial Module

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Overview

The Spatial module provides spatial modeling capabilities for Codomyrmex, including 3D modeling, 4D/Synergetics modeling, and world models for complex system representation.

## Submodules

| Submodule | Description |
|-----------|-------------|
| `three_d/` | Traditional 3D geometric modeling |
| `four_d/` | 4D/Synergetics (Buckminster Fuller concepts) |
| `world_models/` | Complex world model representations |

## Key Features

- **3D Modeling**: Meshes, scenes, geometries, transformations
- **4D/Synergetics**: Higher-dimensional geometric concepts
- **World Models**: Environment and system modeling
- **Coordinate Systems**: Flexible coordinate transformations
- **Visualization**: Export to common 3D formats

## Quick Start

```python
from codomyrmex.spatial import three_d, four_d, world_models

# 3D Modeling
from codomyrmex.spatial.three_d import Scene, Mesh, Vector3

scene = Scene()
cube = Mesh.cube(size=1.0)
cube.translate(Vector3(1, 0, 0))
scene.add(cube)

# Export scene
scene.export("output.obj")

# 4D/Synergetics
from codomyrmex.spatial.four_d import Synergetics

# Create a tetrahedron (basic Synergetics form)
tetra = Synergetics.tetrahedron()

# World Models
from codomyrmex.spatial.world_models import WorldModel, Entity

world = WorldModel()
world.add_entity(Entity(id="sensor_1", position=(0, 0, 0)))
world.simulate(timesteps=100)
```

## 3D Modeling Components

| Component | Description |
|-----------|-------------|
| `Scene` | Container for 3D objects |
| `Mesh` | Geometric mesh (vertices, faces) |
| `Vector3` | 3D vector for positions/directions |
| `Transform` | Translation, rotation, scale |

## 4D/Synergetics Concepts

| Concept | Description |
|---------|-------------|
| `Tetrahedron` | Basic unit in Synergetics |
| `Octahedron` | Dual of the cube |
| `Isotropic Vector Matrix` | IVM coordinate system |

## World Model Components

| Component | Description |
|-----------|-------------|
| `WorldModel` | Container for entities and simulation |
| `Entity` | Object with position and properties |
| `Environment` | Background conditions |

## Navigation

- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: [README](../../../README.md)
