# Coordinates -- Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Coordinate system primitives and transformations supporting cartesian, geographic, polar, and spherical representations. Provides conversion utilities and distance calculations.

## Architecture

```
CoordinateSystem (Enum)
  CARTESIAN | GEOGRAPHIC | POLAR | SPHERICAL

Point(x, y, z, system)
GeoPoint(latitude, longitude, altitude)
BoundingBox(min_point, max_point)

Transform
  +-- convert(point, target_system) -> Point
  +-- to_geographic(point) -> GeoPoint
  +-- from_geographic(geo_point) -> Point

haversine_distance(a: GeoPoint, b: GeoPoint) -> float
```

## Key Classes

### Point

| Field | Type | Notes |
|-------|------|-------|
| `x` | `float` | X coordinate |
| `y` | `float` | Y coordinate |
| `z` | `float` | Z coordinate (default 0.0) |
| `system` | `CoordinateSystem` | Which system these coords represent |

### GeoPoint

| Field | Type | Notes |
|-------|------|-------|
| `latitude` | `float` | Degrees, -90 to 90 |
| `longitude` | `float` | Degrees, -180 to 180 |
| `altitude` | `float` | Meters above sea level (default 0.0) |

### Transform Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `convert(point, target)` | `Point` | System-to-system conversion |
| `to_geographic(point)` | `GeoPoint` | Convert any Point to GeoPoint |
| `from_geographic(geo)` | `Point` | Convert GeoPoint to cartesian Point |

## Dependencies

- `math` (stdlib) for trigonometric calculations
- `enum`, `dataclasses` (stdlib)

## Constraints

- Haversine assumes spherical Earth (radius 6371 km); not ellipsoidal.
- Polar/spherical conversions use standard mathematical conventions.

## Navigation

- [README.md](README.md) | [AGENTS.md](AGENTS.md) | [PAI.md](PAI.md)
- Parent: [spatial](../README.md)
