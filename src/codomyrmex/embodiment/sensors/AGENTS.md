# Codomyrmex Agents — embodiment/sensors

## Purpose

Maintain deterministic sensor data models and the simulated sensor lifecycle
used by the embodiment package.

## Key Files

- [`base.py`](base.py) — sensor readings, connection state, and compatibility
  sensor implementation.
- [`../SPEC.md`](../SPEC.md) — parent embodiment contract.
- [`../../../../tests/unit/embodiment/`](../../../../tests/unit/embodiment/) —
  behavioral tests.

## Dependencies

Only Python standard-library modules are required.

## Development Guidelines

- Keep `SensorData` serializable and explicit about metadata.
- Preserve deterministic default readings for local tests.
- Treat `MockSensor` as a compatibility surface, not evidence of hardware
  integration.
- Add tests for disconnected, default, and metadata behavior.

## Navigation

- [README](README.md)
- [Parent guidance](../AGENTS.md)
