# Coordinates Agentic Context

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Coordinate system definitions and transformations for geographic, cartesian, and polar representations. Agents use these primitives for spatial calculations across the platform.

## Key Components

| Component | Type | Role |
|-----------|------|------|
| `CoordinateSystem` | Enum | CARTESIAN, GEOGRAPHIC, POLAR, SPHERICAL |
| `Point` | Dataclass | x, y, z coordinates with associated system |
| `GeoPoint` | Dataclass | latitude, longitude, altitude for geographic coords |
| `Transform` | Class | Convert between coordinate systems |
| `haversine_distance` | Function | Great-circle distance between two GeoPoints |
| `BoundingBox` | Dataclass | min/max corners defining a spatial region |

## Operating Contracts

- `Transform.convert(point, target_system)` returns a new `Point` in the target system.
- `haversine_distance(a, b)` returns distance in meters using the Haversine formula.
- `BoundingBox.contains(point)` checks spatial membership.
- All coordinate classes are immutable dataclasses.

## Integration Points

- Used by `spatial/three_d` for 3D coordinate handling.
- No MCP tools exposed directly; consumed internally by other spatial modules.

## Navigation

- [README.md](README.md) | [SPEC.md](SPEC.md) | [PAI.md](PAI.md)
- Parent: [spatial](../README.md)
