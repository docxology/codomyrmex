# Spatial Module API Specification

**Version**: v0.1.7 | **Status**: Stable | **Last Updated**: February 2026

## 1. Overview
The `spatial` module provides advanced modeling capabilities for 3D and 4D environments, including support for Synergetics-based geometry and world models.

## 2. Core Components

### 2.1 Submodules
- **`three_d`**: Conventional 3D geometry processing.
- **`four_d`**: 4D space-time and Synergetics modeling.
- **`world_models`**: Cognitive map representations and environmental simulation.
- **`coordinates`**: Coordinate system conversions (Cartesian, spherical, cylindrical, Synergetics, geographic).
- **`physics`**: Physical simulation primitives.
- **`rendering`**: Rendering primitives and scene graph utilities.

## 3. Usage Example

```python
from codomyrmex.spatial.three_d import Mesh, Vector3

p1 = Vector3(0, 0, 0)
p2 = Vector3(1, 1, 1)
print(p1.distance_to(p2))
```
