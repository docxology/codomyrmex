# Embodiment Transformations

## Purpose

This subpackage contains dependency-light three-dimensional vector and rigid
transform utilities for local simulation and test scenarios.

## Components

- [`transformation.py`](transformation.py) defines `Vec3` and `Transform3D`,
  including composition, inversion, Euler-angle conversion, and serialization.

The implementation is a compact local mathematical utility; it is not a claim
of numerical equivalence with a robotics middleware or a production dynamics
engine.

## Validation

Run `uv run pytest tests/unit/embodiment/ -q` and `uv run ruff check src/codomyrmex/embodiment`.

## Navigation

- [Parent module](../README.md)
- [Parent agent guidance](../AGENTS.md)
