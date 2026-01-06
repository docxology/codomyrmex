# spatial

## Signposting
- **Parent**: [codomyrmex](../README.md)
- **Children**:
    - [three_d](three_d/README.md)- **Key Artifacts**:
    - [Agent Guide](AGENTS.md)
    - [Functional Spec](SPEC.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: December 2025

## Overview

The spatial module provides 3D/4D visualization, modeling, and world model capabilities for the Codomyrmex platform. It consolidates all spatial computing functionality into a unified module.

## Submodules

### three_d/
Core 3D modeling and visualization. Includes scene building, mesh generation, and rendering capabilities.

### four_d/
Temporal (4D) modeling for time-series spatial data. Currently in planning.

### world_models/
World model representations and simulations. Currently in planning.

## Usage

```python
from codomyrmex.spatial.three_d import SceneBuilder, MeshGenerator

# Create a scene
scene = SceneBuilder()
mesh = MeshGenerator.create_cube(size=1.0)
scene.add_mesh(mesh)

# Render
image = scene.render()
```

## Navigation Links

- **Parent**: [codomyrmex](../README.md)
- **3D Documentation**: [three_d/README.md](three_d/README.md)
