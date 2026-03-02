# Agent Guidelines - Spatial

**Version**: v1.0.5 | **Status**: Active | **Last Updated**: March 2026

## Module Overview

3D/4D spatial modeling, physics, coordinates, and rendering.

## Key Submodules

- **three_d** — 3D geometry: Vec3, Quaternion, Mesh, Transform
- **four_d** — 4D Synergetics modeling
- **coordinates** — Coordinate systems and projections
- **rendering** — Visualization and rendering
- **physics** — Physics simulation, rigid bodies
- **world_models** — Spatial world representations

## Agent Instructions

1. **Use Vec3 for positions** — All 3D positions should use `Vec3` class
2. **Quaternions for rotation** — Avoid Euler angles; use `Quaternion` for rotation
3. **Coordinate transforms** — Use `Transform3D` for position + rotation + scale
4. **Choose projection** — Use appropriate projection (mercator, orthographic, perspective)
5. **Physics timestep** — Use fixed timestep for deterministic physics

## Common Patterns

```python
from codomyrmex.spatial.three_d import Vec3, Quaternion, Mesh

# Create positioned mesh
mesh = Mesh.cube(size=1.0)
mesh.position = Vec3(1, 2, 3)
mesh.rotation = Quaternion.from_euler(0, 45, 0)

# Coordinate conversion
from codomyrmex.spatial.coordinates import GeoCoordinate
geo = GeoCoordinate(lat=37.7749, lon=-122.4194)
cartesian = geo.to_cartesian()
```

## Testing Patterns

```python
# Verify vector operations
v1 = Vec3(1, 0, 0)
v2 = Vec3(0, 1, 0)
assert v1.dot(v2) == 0  # Perpendicular

# Verify quaternion rotation
q = Quaternion.from_euler(0, 90, 0)
rotated = q.rotate(Vec3(1, 0, 0))
assert abs(rotated.z - 1.0) < 0.001  # Rotated 90° around Y
```

## PAI Agent Role Access Matrix

| PAI Agent | Access Level | Primary Capabilities | Trust Level |
|-----------|-------------|---------------------|-------------|
| **Engineer** | Full | Direct Python import, class instantiation, full API access | TRUSTED |
| **Architect** | Read + Design | API review, interface design, dependency analysis | OBSERVED |
| **QATester** | Validation | Integration testing via pytest, output validation | OBSERVED |

### Engineer Agent
**Use Cases**: Performs spatial analysis, GIS operations, and geospatial queries using `Vec3`, `Quaternion`, `Mesh`, `GeoCoordinate`, and physics simulation classes. Handles coordinate transformations and 3D/4D modeling.

### Architect Agent
**Use Cases**: Designs spatial data models, reviews coordinate system choices (mercator, orthographic, perspective), evaluates quaternion vs. Euler angle trade-offs, and plans physics timestep strategies.

### QATester Agent
**Use Cases**: Validates coordinate transformations and spatial queries, verifies vector operation correctness (dot products, cross products), confirms quaternion rotation accuracy, and tests geo-coordinate round-trip conversions.

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)
