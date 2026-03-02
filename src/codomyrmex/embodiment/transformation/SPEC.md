# Coordinate Transformations -- Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

3D rigid-body transformation utilities for embodied systems. Provides translation, ZYX Euler rotation, composition, inverse computation, and point/vector transformation in right-hand coordinate frames.

## Architecture

Pure-math implementation using nested lists as 3x3 rotation matrices (no NumPy dependency). `Vec3` is an immutable frozen dataclass for 3D vectors with arithmetic operators. `Transform3D` combines translation and rotation with matrix-based composition for chaining transforms.

## Key Classes

### `Vec3` (Frozen Dataclass)

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `__add__` | `other: Vec3` | `Vec3` | Element-wise vector addition |
| `__sub__` | `other: Vec3` | `Vec3` | Element-wise vector subtraction |
| `__mul__` | `scalar: float` | `Vec3` | Scalar multiplication |
| `length` | -- | `float` | Euclidean magnitude |
| `normalized` | -- | `Vec3` | Unit vector (returns zero vector if magnitude < 1e-12) |
| `dot` | `other: Vec3` | `float` | Dot product |
| `cross` | `other: Vec3` | `Vec3` | Cross product (right-hand rule) |
| `to_tuple` | -- | `tuple[float, float, float]` | Convert to tuple |
| `to_dict` | -- | `dict[str, float]` | Serialize to `{x, y, z}` dict |

### `Transform3D`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `__init__` | `translation?, rotation?` | -- | Create from (x,y,z) translation and (roll,pitch,yaw) radians |
| `transform_point` | `point: tuple` | `tuple` | Apply rotation then translation to a 3D point |
| `transform_vector` | `vector: tuple` | `tuple` | Apply rotation only (no translation) to a direction vector |
| `compose` | `other: Transform3D` | `Transform3D` | Compose transforms: self then other (matrix multiplication) |
| `inverse` | -- | `Transform3D` | Compute inverse transform (R^T, -R^T * t) |
| `identity` | -- | `Transform3D` | Class method: no rotation, no translation |
| `from_translation` | `x, y, z` | `Transform3D` | Class method: pure translation |
| `from_yaw` | `yaw_rad` | `Transform3D` | Class method: pure Z-axis rotation |
| `deg_to_rad` | `deg: float` | `float` | Static: degrees to radians |
| `rad_to_deg` | `rad: float` | `float` | Static: radians to degrees |
| `to_dict` | -- | `dict` | Serialize to JSON-compatible dict |

## Dependencies

- **Internal**: None
- **External**: None (Python stdlib: `math`, `dataclasses`)

## Constraints

- Rotation order is ZYX (yaw-pitch-roll), following aerospace convention.
- Euler angle extraction uses `asin` with clamping to [-1, 1] to avoid domain errors near gimbal lock.
- Gimbal lock fallback sets roll to 0 when cos(pitch) is near zero.
- `Vec3.normalized()` returns zero vector for near-zero magnitude (threshold: 1e-12).
- Zero-mock: real computations only, `NotImplementedError` for unimplemented paths.

## Error Handling

- No custom exceptions; relies on Python's built-in `ValueError` and `TypeError` for invalid inputs.
- All errors logged before propagation.
