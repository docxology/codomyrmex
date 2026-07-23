# Codomyrmex Agents — embodiment/actuators

## Purpose

Maintain the local simulated actuator contract used by embodiment tests and
examples. The implementation is a dependency-light compatibility surface, not
a physical-device driver.

## Key Files

- [`base.py`](base.py) — command/status dataclasses and simulated lifecycle.
- [`../SPEC.md`](../SPEC.md) — parent embodiment contract.
- [`../../../../tests/unit/embodiment/`](../../../../tests/unit/embodiment/) —
  behavioral tests.

## Dependencies

Only Python standard-library modules are required.

## Development Guidelines

- Keep command execution deterministic and side-effect free outside the object.
- Preserve actuator identity checks and disconnected-state behavior.
- Add real local tests for new behavior; do not introduce mocks or hardware
  network calls.
- Document compatibility aliases as non-primary APIs.

## Navigation

- [README](README.md)
- [Parent guidance](../AGENTS.md)
