# Spatial Configuration

**Version**: v1.1.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Spatial computing with 2D/3D geometry, coordinate systems, and spatial indexing. Provides geospatial operations and 3D transformation utilities.

## Configuration Options

The spatial module operates with sensible defaults and does not require environment variable configuration. Coordinate reference systems and spatial index parameters are set per-instance. 3D rendering requires optional dependencies.

## PAI Integration

PAI agents interact with spatial through direct Python imports. Coordinate reference systems and spatial index parameters are set per-instance. 3D rendering requires optional dependencies.

## Validation

```bash
# Verify module is available
codomyrmex modules | grep spatial

# Run module health check
codomyrmex status
```

## Navigation

- [Source Module](../../src/codomyrmex/spatial/README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md)
