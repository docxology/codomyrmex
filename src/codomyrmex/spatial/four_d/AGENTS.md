# Codomyrmex Agents — src/codomyrmex/spatial/four_d

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose

Provides 4D modeling capabilities based on Buckminster Fuller's Synergetics, including Quadray coordinate systems, Isotropic Vector Matrix (IVM), and Close Packed Spheres (CPS) structures for geometric modeling beyond traditional Cartesian coordinates.

## Active Components

- `__init__.py` - Module implementation with core classes
- `SPEC.md` - Module specification
- `README.md` - Module documentation

## Key Classes and Functions

### QuadrayCoordinate
4-dimensional coordinate system using four basis vectors pointing to tetrahedron vertices:
- `__init__(a, b, c, d)` - Initialize with four quadray values
- `coords` - Tuple of (a, b, c, d) values
- Represents points as positive combinations of four basis vectors

### IsotropicVectorMatrix
Represents the IVM structure (space-filling tetrahedra and octahedra):
- Models space as a grid of equilateral triangular faces
- Provides alternative to cubic space-filling
- Used for efficient spatial subdivision

### ClosePackedSphere
Models spheres in closest-packed arrangements:
- Face-centered cubic (FCC) packing
- Hexagonal close packing (HCP)
- Sphere center coordinates and neighbor relationships

### synergetics_transform(coord_3d)
Transforms standard 3D Cartesian coordinates to 4D Synergetic coordinates:
- Input: 3D (x, y, z) coordinate
- Output: Quadray representation

## Synergetics Concepts

### Quadray System
- Four basis vectors from origin to tetrahedron vertices
- Any point expressible with non-negative coordinates
- Eliminates negative numbers in coordinate representation

### IVM (Isotropic Vector Matrix)
- Closest-packing of spheres creates octahedra and tetrahedra
- All vectors same length (isotropic)
- More efficient than cubic for certain geometric computations

## Operating Contracts

- Quadray coordinates normalized to ensure valid representation
- Transform functions handle degenerate cases
- Coordinate systems are convertible (Cartesian <-> Quadray)
- Implementation follows Fuller's Synergetics conventions

## Signposting

- **References**: Buckminster Fuller's "Synergetics" (1975, 1979)
- **Parent Directory**: [spatial](../README.md) - Parent module documentation
- **Related Modules**:
  - `three_d/` - Traditional 3D modeling
  - `world_models/` - Agent spatial reasoning
- **Project Root**: [../../../../README.md](../../../../README.md) - Main project documentation
