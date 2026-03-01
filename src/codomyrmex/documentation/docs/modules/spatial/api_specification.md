# Spatial Module API Specification

**Version**: v0.1.7 | **Status**: Stable | **Last Updated**: February 2026

## 1. Overview

The `spatial` module provides advanced modeling capabilities for 3D and 4D environments, including support for Synergetics-based geometry, coordinate transformations, and world models. It exposes six submodules covering conventional 3D, 4D/Synergetics, coordinate systems, world models, physics, and rendering.

## 2. Core Components

### 2.1 Submodules

| Submodule | Purpose | Key Exports |
|-----------|---------|-------------|
| `coordinates` | Coordinate system types and transformations | `Point3D`, `SphericalCoord`, `CylindricalCoord`, `GeographicCoord`, `Matrix4x4`, `CoordinateTransformer`, `CoordinateSystem` |
| `three_d` | 3D scene graph and AR/VR/XR support | `Scene3D`, `Object3D`, `Camera3D`, `Light3D`, `Material3D`, `RenderPipeline`, `MeshLoader` |
| `four_d` | Synergetics / 4D modeling | `QuadrayCoordinate`, `IsotropicVectorMatrix`, `ClosePackedSphere`, `synergetics_transform` |
| `world_models` | Cognitive map and environmental simulation | (planned) |
| `physics` | Physical simulation primitives | (planned) |
| `rendering` | Rendering primitives and scene graph utilities | (planned) |

### 2.2 Module Exports

```python
from codomyrmex.spatial import (
    coordinates,
    three_d,
    four_d,
    world_models,
    physics,
    rendering,
    cli_commands,
)
```

## 3. `coordinates` Submodule

### 3.1 `CoordinateSystem` (Enum)

```python
class CoordinateSystem(Enum):
    CARTESIAN   = "cartesian"
    SPHERICAL   = "spherical"
    CYLINDRICAL = "cylindrical"
    GEOGRAPHIC  = "geographic"   # lat/lon
    UTM         = "utm"
```

### 3.2 `Point3D` (dataclass)

The primary 3D vector/point type used throughout the spatial module.

```python
@dataclass
class Point3D:
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0

    # Arithmetic operators: +, -, *, /
    def magnitude(self) -> float: ...
    def normalize(self) -> 'Point3D': ...
    def dot(self, other: 'Point3D') -> float: ...
    def cross(self, other: 'Point3D') -> 'Point3D': ...
    def distance_to(self, other: 'Point3D') -> float: ...
    def to_tuple(self) -> tuple[float, float, float]: ...

    @classmethod
    def from_tuple(cls, t: tuple[float, float, float]) -> 'Point3D': ...
```

### 3.3 `SphericalCoord` (dataclass)

```python
@dataclass
class SphericalCoord:
    r: float = 0.0      # radius
    theta: float = 0.0  # azimuthal angle (0 to 2π)
    phi: float = 0.0    # polar angle (0 to π)

    def to_cartesian(self) -> Point3D: ...
    @classmethod
    def from_cartesian(cls, point: Point3D) -> 'SphericalCoord': ...
```

### 3.4 `CylindricalCoord` (dataclass)

```python
@dataclass
class CylindricalCoord:
    r: float = 0.0      # radius in xy-plane
    theta: float = 0.0  # azimuthal angle
    z: float = 0.0      # height

    def to_cartesian(self) -> Point3D: ...
    @classmethod
    def from_cartesian(cls, point: Point3D) -> 'CylindricalCoord': ...
```

### 3.5 `GeographicCoord` (dataclass)

```python
@dataclass
class GeographicCoord:
    lat: float = 0.0    # latitude in degrees (-90 to 90)
    lon: float = 0.0    # longitude in degrees (-180 to 180)
    alt: float = 0.0    # altitude in meters

    EARTH_RADIUS = 6371000  # meters

    def to_cartesian(self) -> Point3D: ...             # ECEF Cartesian
    def distance_to(self, other: 'GeographicCoord') -> float: ...  # Haversine
    def bearing_to(self, other: 'GeographicCoord') -> float: ...   # degrees

    @classmethod
    def from_cartesian(cls, point: Point3D) -> 'GeographicCoord': ...
```

### 3.6 `Matrix4x4` (dataclass)

```python
@dataclass
class Matrix4x4:
    data: list[list[float]]   # 4×4, default = identity

    @classmethod
    def identity(cls) -> 'Matrix4x4': ...
    @classmethod
    def translation(cls, tx: float, ty: float, tz: float) -> 'Matrix4x4': ...
    @classmethod
    def scale(cls, sx: float, sy: float, sz: float) -> 'Matrix4x4': ...
    @classmethod
    def rotation_x(cls, angle: float) -> 'Matrix4x4': ...  # radians
    @classmethod
    def rotation_y(cls, angle: float) -> 'Matrix4x4': ...
    @classmethod
    def rotation_z(cls, angle: float) -> 'Matrix4x4': ...

    def __mul__(self, other: 'Matrix4x4') -> 'Matrix4x4': ...
    def transform_point(self, point: Point3D) -> Point3D: ...
```

### 3.7 `CoordinateTransformer`

Static utility class for coordinate system conversions:

```python
class CoordinateTransformer:
    @staticmethod
    def cartesian_to_spherical(point: Point3D) -> SphericalCoord: ...
    @staticmethod
    def spherical_to_cartesian(coord: SphericalCoord) -> Point3D: ...
    @staticmethod
    def cartesian_to_cylindrical(point: Point3D) -> CylindricalCoord: ...
    @staticmethod
    def cylindrical_to_cartesian(coord: CylindricalCoord) -> Point3D: ...
    @staticmethod
    def geographic_to_cartesian(coord: GeographicCoord) -> Point3D: ...  # ECEF
    @staticmethod
    def cartesian_to_geographic(point: Point3D) -> GeographicCoord: ...
    @staticmethod
    def degrees_to_radians(degrees: float) -> float: ...
    @staticmethod
    def radians_to_degrees(radians: float) -> float: ...
```

## 4. `three_d` Submodule

3D scene graph, AR/VR/XR support, and rendering pipeline. Exports via star imports from `engine_3d`, `ar_vr_support`, and `rendering_pipeline` submodules.

```python
from codomyrmex.spatial.three_d import (
    # Scene graph
    Scene3D, Object3D, Camera3D, Light3D, Material3D,
    # AR/VR/XR
    ARSession, VRRenderer, XRInterface,
    # Rendering
    RenderPipeline, ShaderManager, TextureManager,
    # Utilities
    MeshLoader, AnimationController, PhysicsEngine,
)
```

## 5. `four_d` Submodule (Synergetics)

```python
class QuadrayCoordinate:
    """4-vector Quadray coordinate (a, b, c, d)."""
    def __init__(self, a: float = 0, b: float = 0, c: float = 0, d: float = 0): ...
    coords: tuple[float, float, float, float]

class IsotropicVectorMatrix:
    """Isotropic Vector Matrix (IVM) structure — planned."""
    pass

class ClosePackedSphere:
    """Sphere in a close-packed arrangement — planned."""
    pass

def synergetics_transform(coord_3d) -> None:
    """Transform 3D coordinates to 4D Synergetics coordinates — planned."""
    pass
```

> **Note:** `IsotropicVectorMatrix`, `ClosePackedSphere`, and `synergetics_transform` are scaffolded for future implementation.

## 6. CLI Integration

```python
from codomyrmex.spatial import cli_commands

commands = cli_commands()
# commands["coordinate_systems"]()  → lists all 5 coordinate system names
# commands["status"]()              → prints availability of each submodule
```

## 7. Usage Examples

```python
# Coordinate transformations
from codomyrmex.spatial.coordinates import Point3D, CoordinateTransformer, GeographicCoord

origin = Point3D(0, 0, 0)
p = Point3D(3, 4, 0)
print(p.magnitude())          # 5.0
print(p.distance_to(origin))  # 5.0
print(p.normalize())          # Point3D(0.6, 0.8, 0.0)

geo = GeographicCoord(lat=37.7749, lon=-122.4194, alt=0)  # San Francisco
ecef = geo.to_cartesian()
```

```python
# 4D Synergetics
from codomyrmex.spatial.four_d import QuadrayCoordinate

q = QuadrayCoordinate(1, 0, 0, 0)
print(q.coords)  # (1, 0, 0, 0)
```

```python
# Matrix transformations
from codomyrmex.spatial.coordinates import Matrix4x4, Point3D
import math

rot = Matrix4x4.rotation_z(math.pi / 4)  # 45-degree rotation
p = Point3D(1, 0, 0)
rotated = rot.transform_point(p)
```

## 8. Error Handling

- `ImportError`: Raised if optional SDK dependencies (e.g., NumPy for physics) are unavailable. Use `uv sync --extra spatial` to install.
- `ZeroDivisionError` guard in `normalize()`: returns `Point3D(0, 0, 0)` for zero-magnitude vectors.
- Submodules with `pass`-bodied classes (`IsotropicVectorMatrix`, `ClosePackedSphere`) will raise `NotImplementedError` if methods are called on future-only interfaces.

## 9. Configuration

No environment variables required for core coordinate and geometry operations. Optional submodules (`physics`, `rendering`) may require external SDK configuration — see their respective README files.
