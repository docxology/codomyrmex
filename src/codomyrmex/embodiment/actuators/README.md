# Embodiment Actuators

## Purpose

This subpackage provides deterministic local actuator interfaces for simulations,
tests, and demonstrations. It does not claim to drive physical hardware.

## Components

- [`base.py`](base.py) defines `ActuatorCommand`, `ActuatorStatus`, and the
  `SimulatedActuator` lifecycle.
- `MockActuator` remains a compatibility alias with the historical metadata
  surface; new code should prefer `SimulatedActuator`.

## Validation

Run `uv run pytest tests/unit/embodiment/ -q` from the repository root. Keep
actuator tests local, deterministic, and zero-mock.

## Navigation

- [Parent module](../README.md)
- [Parent agent guidance](../AGENTS.md)
