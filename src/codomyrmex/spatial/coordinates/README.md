# Coordinates

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Coordinate transformation utilities for spatial modeling. Provides coordinate system representations (Cartesian, spherical, cylindrical, geographic) with bidirectional conversions, 3D vector arithmetic, 4x4 homogeneous transformation matrices, and geographic distance/bearing calculations via the Haversine formula.

## Key Exports

### Enums

- **`CoordinateSystem`** -- Supported coordinate systems: CARTESIAN, SPHERICAL, CYLINDRICAL, GEOGRAPHIC, UTM

### Coordinate Types

- **`Point3D`** -- 3D Cartesian point/vector with arithmetic operators (+, -, *, /), magnitude, normalization, dot product, cross product, distance, and tuple conversion
- **`SphericalCoord`** -- Spherical coordinates (r, theta, phi) with bidirectional Cartesian conversion
- **`CylindricalCoord`** -- Cylindrical coordinates (r, theta, z) with bidirectional Cartesian conversion
- **`GeographicCoord`** -- Geographic coordinates (lat, lon, alt) with ECEF Cartesian conversion, Haversine great-circle distance, and initial bearing calculation

### Transformation

- **`Matrix4x4`** -- 4x4 homogeneous transformation matrix with factory methods for identity, translation, scale, and rotation (X/Y/Z axes); supports matrix multiplication and point transformation
- **`CoordinateTransformer`** -- Static utility class providing all pairwise coordinate conversions and degree/radian helpers

## Directory Contents

- `__init__.py` - All coordinate types and transformer (327 lines)
- `py.typed` - PEP 561 type stub marker

## Usage

```python
from codomyrmex.spatial.coordinates import Point3D, GeographicCoord, Matrix4x4
import math

# 3D vector operations
a = Point3D(1, 2, 3)
b = Point3D(4, 5, 6)
print(a.cross(b))        # Cross product
print(a.distance_to(b))  # Euclidean distance

# Geographic distance
zurich = GeographicCoord(lat=47.3769, lon=8.5417)
geneva = GeographicCoord(lat=46.2044, lon=6.1432)
print(f"{zurich.distance_to(geneva) / 1000:.1f} km")

# Transformation matrix
rot = Matrix4x4.rotation_z(math.pi / 4)
translated = Matrix4x4.translation(10, 0, 0)
combined = rot * translated
result = combined.transform_point(Point3D(1, 0, 0))
```

## Navigation

- **Parent Module**: [spatial](../README.md)
- **Project Root**: [../../../../README.md](../../../../README.md)
