# Spatial Module Documentation

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Spatial modeling module for Codomyrmex.

## Submodules

| Submodule | Description |
|-----------|-------------|
| `coordinates` | Coordinate transformation utilities for spatial modeling. |
| `four_d` | 4D modeling module (Synergetics) for Codomyrmex. |
| `physics` | Physics Simulation submodule. |
| `rendering` | Spatial Rendering submodule. |
| `three_d` | Spatial 3D Modeling and Rendering Module for Codomyrmex. |
| `world_models` | World modeling module for Codomyrmex. |


## Installation

```bash
pip install codomyrmex
```

## Quick Start

```python
from codomyrmex.spatial import *  # See source for specific imports
```

## Directory Contents

| File | Description |
|------|-------------|
| `README.md` | This documentation |
| `AGENTS.md` | Agent coordination guide |
| `SPEC.md` | Technical specification |

## Navigation

- **Source**: [src/codomyrmex/spatial/](../../../src/codomyrmex/spatial/)
- **Parent**: [Modules](../README.md)

## Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k spatial -v
```
