# Spatial Documentation

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Geospatial and spatial data processing utilities.

## Key Features

- **Geo** — Geographic operations
- **Coordinates** — Coordinate systems
- **Distance** — Distance calculations
- **Indexing** — Spatial indexing

## Quick Start

```python
from codomyrmex.spatial import GeoPoint, distance

point1 = GeoPoint(lat=37.7749, lon=-122.4194)
point2 = GeoPoint(lat=34.0522, lon=-118.2437)

dist = distance(point1, point2)
print(f"Distance: {dist:.2f} km")
```

## Directory Contents

| File | Description |
|------|-------------|
| `README.md` | This file |
| `SPEC.md` | Technical specification |

## Navigation

- **Source**: [src/codomyrmex/spatial/](../../../src/codomyrmex/spatial/)
- **Parent**: [Modules](../README.md)
