# Embodiment Sensors

## Purpose

This subpackage provides deterministic local sensor readings for simulations,
tests, and examples. It is intentionally separate from physical sensor drivers.

## Components

- [`base.py`](base.py) defines `SensorData`, `SimulatedSensor`, and the
  historical `MockSensor` compatibility surface.

## Validation

Run `uv run pytest tests/unit/embodiment/ -q` from the repository root. Keep
fixtures local and avoid environment-dependent timestamps in assertions.

## Navigation

- [Parent module](../README.md)
- [Parent agent guidance](../AGENTS.md)
