# Personal AI Infrastructure — Spatial Module

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The Spatial module provides PAI integration for geospatial operations.

## PAI Capabilities

### Geospatial Operations

Work with coordinates:

```python
from codomyrmex.spatial import GeoPoint, distance

point1 = GeoPoint(lat=37.7749, lon=-122.4194)
point2 = GeoPoint(lat=34.0522, lon=-118.2437)

dist = distance(point1, point2)
print(f"Distance: {dist:.2f} km")
```

### Spatial Indexing

Index spatial data:

```python
from codomyrmex.spatial import SpatialIndex

index = SpatialIndex()
index.add(point, data)
nearby = index.query_radius(center, radius=10)
```

## PAI Integration Points

| Component | PAI Use Case |
|-----------|-------------|
| `GeoPoint` | Coordinates |
| `distance` | Calculate distance |
| `SpatialIndex` | Spatial queries |

## Navigation

- [README](README.md) | [AGENTS](AGENTS.md) | [SPEC](SPEC.md)
