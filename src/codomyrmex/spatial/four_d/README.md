# four_d

## Signposting
- **Parent**: [spatial](../README.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [Agent Guide](AGENTS.md)
    - [Functional Spec](SPEC.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Overview

4D modeling (Synergetics) including time-series spatial data, animation sequences, temporal interpolation, and four-dimensional coordinate systems (Quadray coordinates, Isotropic Vector Matrix).

## Directory Contents
- `__init__.py` – File

## Navigation
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Parent Directory**: [spatial](../README.md)
- **Project Root**: [README](../../../../README.md)

## Getting Started

To use this module in your project, import the necessary components:

```python
from codomyrmex.spatial.four_d import (
    QuadrayCoordinate,
    IsotropicVectorMatrix,
)

# Work with Quadray coordinates (4D)
coord = QuadrayCoordinate(a=1, b=2, c=3, d=4)
print(f"Quadray: {coord}")
print(f"Magnitude: {coord.magnitude()}")

# Use Isotropic Vector Matrix for 4D transformations
ivm = IsotropicVectorMatrix()
transformed = ivm.transform(coord, transformation="rotation")
print(f"Transformed: {transformed}")

# Temporal interpolation
from codomyrmex.spatial.four_d import interpolate_temporal
result = interpolate_temporal(
    start_state=coord,
    end_state=QuadrayCoordinate(a=2, b=3, c=4, d=5),
    t=0.5
)
```

