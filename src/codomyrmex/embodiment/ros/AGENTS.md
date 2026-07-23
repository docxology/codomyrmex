# Codomyrmex Agents — embodiment/ros

## Purpose

Maintain the local ROS-style pub/sub compatibility surface used by the
embodiment package. It intentionally has no external ROS dependency.

## Key Files

- [`ros_bridge.py`](ros_bridge.py) — topic state, publication, subscription,
  latching, and bounded history.
- [`../SPEC.md`](../SPEC.md) — parent package contract.
- [`../../../../tests/unit/embodiment/`](../../../../tests/unit/embodiment/) —
  behavioral tests.

## Dependencies

The bridge uses Python standard-library `asyncio`, collections, dataclasses,
and typing utilities.

## Development Guidelines

- Preserve asynchronous handler support and bounded topic history.
- Keep delivery local and deterministic; do not imply ROS2 transport semantics.
- Exercise both synchronous and asynchronous handlers with real tests.
- Close or discard test event-loop resources cleanly.

## Navigation

- [README](README.md)
- [Parent guidance](../AGENTS.md)
