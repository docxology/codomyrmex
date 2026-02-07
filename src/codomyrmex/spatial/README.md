# Spatial Module

**Version**: v0.1.0 | **Status**: Active

3D/4D spatial modeling, coordinates, physics, and rendering.


## Installation

```bash
pip install codomyrmex
```

Or for development:

```bash
uv sync
```

## Key Exports

### Submodules
- **`coordinates/`** — Coordinate transformation utilities for spatial modeling.
- **`four_d/`** — 4D modeling module (Synergetics) for Codomyrmex.
- **`physics/`** — Physics Simulation submodule.
- **`rendering/`** — Spatial Rendering submodule.
- **`three_d/`** — Spatial 3D Modeling and Rendering Module for Codomyrmex.
- **`world_models/`** — World modeling module for Codomyrmex.

## Quick Start

```python
from codomyrmex.spatial import three_d, four_d, coordinates, physics, rendering

# 3D modeling
from codomyrmex.spatial.three_d import Mesh, Vec3, Quaternion

mesh = Mesh.cube(size=1.0)
mesh.translate(Vec3(1, 0, 0))
mesh.rotate(Quaternion.from_euler(45, 0, 0))

# Coordinate systems
from codomyrmex.spatial.coordinates import GeoCoordinate, ScreenCoordinate

geo = GeoCoordinate(lat=37.7749, lon=-122.4194, alt=0)
screen = geo.to_screen(projection="mercator")

# Physics simulation
from codomyrmex.spatial.physics import RigidBody, World

world = World(gravity=Vec3(0, -9.81, 0))
body = RigidBody(mass=1.0, position=Vec3(0, 10, 0))
world.add(body)
world.step(dt=0.016)
```

## Submodules

| Module | Description |
|--------|-------------|
| `three_d` | 3D geometry, meshes, vectors, quaternions |
| `four_d` | 4D Synergetics modeling |
| `coordinates` | Coordinate systems and projections |
| `rendering` | Visualization and rendering |
| `physics` | Physics simulation and rigid bodies |
| `world_models` | Spatial world representations |


## Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k spatial -v
```


## Documentation

- [Module Documentation](../../../docs/modules/spatial/README.md)
- [Agent Guide](../../../docs/modules/spatial/AGENTS.md)
- [Specification](../../../docs/modules/spatial/SPEC.md)

## Navigation

- [SPEC](SPEC.md) | [AGENTS](AGENTS.md) | [PAI](PAI.md)
