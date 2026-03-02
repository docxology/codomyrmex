# Ideoscape -- Technical Specification

**Version**: v1.0.0 | **Status**: Experimental | **Last Updated**: March 2026

## Overview

Models information landscapes as 2D terrain maps using Gaussian kernel density estimation. Features (memes, concepts, events) are placed in a coordinate system and rendered as height-map elevations representing attention or virality intensity. Supports multi-layer compositing for thematic filtering.

## Architecture

Gaussian kernel terrain generation pattern. `MapFeature` points are projected onto a 2D grid, and each feature contributes a Gaussian peak proportional to its `magnitude`. `IdeoscapeEngine` renders individual layers and composites multiple layers via weighted additive blending.

## Key Classes

### `IdeoscapeEngine`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `render_layer` | `layer: IdeoscapeLayer, resolution: int` | `TerrainMap` | Render a single layer into a terrain height map |
| `composite` | `layers: list[IdeoscapeLayer]` | `TerrainMap` | Combine multiple layers via opacity-weighted additive blending |

### Data Models

| Class | Fields | Purpose |
|-------|--------|---------|
| `MapFeature` | `name, position: np.ndarray, feature_type, magnitude, metadata` | A point on the ideoscape map |
| `IdeoscapeLayer` | `name, data_points: list[MapFeature], opacity` | A thematic layer of features with visual weight |
| `TerrainMap` | `height_map: np.ndarray, resolution, features, timestamp` | Generated 2D terrain with identified features |
| `CoordinateSystem` | `dimensions, bounds, projection` | Mapping space definition |
| `ProjectionType` | `MERCATOR, HYPERBOLIC, TOROIDAL, SPHERICAL` | Map projection type enum |

### Module Functions

| Function | Parameters | Returns | Description |
|----------|-----------|---------|-------------|
| `generate_terrain` | `features: list[MapFeature], resolution, bounds` | `TerrainMap` | Generate height map from features using Gaussian kernels (sigma=10.0) |
| `locate_features` | `terrain: TerrainMap, threshold: float` | `list[tuple[int, int]]` | Find grid coordinates of peaks above threshold |

## Dependencies

- **Internal**: None (self-contained within `meme` package)
- **External**: `numpy` (array math, meshgrid, Gaussian kernel computation)

## Constraints

- Fixed Gaussian sigma of 10.0 for all features (not configurable per feature).
- Default bounds are [-100, 100, -100, 100]; default resolution is 100x100 grid.
- `MapFeature.position` must have at least 2 coordinates; features with fewer are skipped.
- Compositing is simple additive (no normalization); overlapping layers may saturate.
- Zero-mock: real data only, `NotImplementedError` for unimplemented paths.

## Error Handling

- `composite` returns an empty 100x100 zero array when given no layers.
- `MapFeature.__post_init__` converts list positions to numpy arrays automatically.
