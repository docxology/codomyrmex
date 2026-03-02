# Codomyrmex Agents -- src/codomyrmex/meme/ideoscape

**Version**: v1.0.0 | **Status**: Experimental | **Last Updated**: March 2026

## Purpose

Models information landscapes as 2D terrain maps using Gaussian kernel density estimation. Features (memes, concepts, events) are rendered as height-map elevations representing attention or virality intensity. Supports multi-layer compositing with opacity weighting for thematic filtering.

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `engine.py` | `IdeoscapeEngine` | Orchestrator rendering layers and compositing terrain maps |
| `cartography.py` | `generate_terrain` | Generate height map from feature points using Gaussian kernels |
| `cartography.py` | `locate_features` | Find grid coordinates of peaks above a threshold |
| `models.py` | `MapFeature` | A point on the map with position, type, and magnitude |
| `models.py` | `IdeoscapeLayer` | A thematic layer of features with opacity weighting |
| `models.py` | `TerrainMap` | Generated 2D height map with resolution and features |
| `models.py` | `CoordinateSystem` | Mapping space definition with dimensions and bounds |
| `models.py` | `ProjectionType` | MERCATOR, HYPERBOLIC, TOROIDAL, SPHERICAL |

## Operating Contracts

- Fixed Gaussian sigma of 10.0 for all features; not configurable per feature.
- Default grid is 100x100 over [-100, 100] bounds in both dimensions.
- `MapFeature.position` must have at least 2 coordinates; features with fewer are silently skipped.
- Compositing is additive (no normalization); overlapping layers may produce large values.
- `composite` returns an empty 100x100 zero array when given no layers.
- Errors must be logged via `logging_monitoring` before re-raising.

## Integration Points

- **Depends on**: `numpy` (external)
- **Used by**: `meme.rhizome` (rhizome defines paths, ideoscape defines terrain intensity), `meme.contagion` (cascade intensity visualization)

## Navigation

- **Parent**: [meme](../README.md)
- **Root**: [Root](../../../../README.md)
