# Codomyrmex Agents — embodiment/transformation

## Purpose

Maintain deterministic vector and rigid-transform helpers used by local
embodiment simulations. Numerical behavior should remain explicit and small in
scope.

## Key Files

- [`transformation.py`](transformation.py) — `Vec3`, `Transform3D`, and matrix
  helpers.
- [`../SPEC.md`](../SPEC.md) — parent embodiment contract.
- [`../../../../tests/unit/embodiment/`](../../../../tests/unit/embodiment/) —
  behavioral tests.

## Dependencies

Only Python's `math` module and standard typing/collection utilities are used.

## Development Guidelines

- Test composition and inverse operations with tolerances appropriate to
  floating-point arithmetic.
- Preserve the documented roll/pitch/yaw convention.
- Keep zero-vector normalization defined and deterministic.
- Do not describe these helpers as a physical simulator or robotics proof.

## Navigation

- [README](README.md)
- [Parent guidance](../AGENTS.md)
