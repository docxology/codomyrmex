# Codomyrmex Agents — src/codomyrmex/spatial/four_d

## Signposting
- **Parent**: [spatial](../AGENTS.md)
- **Self**: [Agents](AGENTS.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [Functional Spec](SPEC.md)
    - [Human Readme](README.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose
4D modeling (Synergetics) including time-series spatial data, animation sequences, temporal interpolation, and four-dimensional coordinate systems (Quadray coordinates, Isotropic Vector Matrix).

## Active Components
- `__init__.py` – Module exports and public API

## Key Classes and Functions

### QuadrayCoordinate (`__init__.py`)
- `QuadrayCoordinate(a: float, b: float, c: float, d: float)` – Four-dimensional coordinate system
- `coords: tuple` – Coordinate tuple (a, b, c, d)

### IsotropicVectorMatrix (`__init__.py`)
- `IsotropicVectorMatrix()` – Isotropic vector matrix operations

## Operating Contracts
- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.

## Navigation Links
- **Human Documentation**: [README.md](README.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **📁 Parent Directory**: [spatial](../README.md) - Parent directory documentation
- **🏠 Project Root**: [README](../../../../README.md) - Main project documentation