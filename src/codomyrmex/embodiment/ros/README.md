# Embodiment ROS-Style Bridge

## Purpose

`ROS2Bridge` is an in-process, asynchronous topic bridge for local simulations,
tests, and examples. It provides topic creation, publication, subscription,
bounded history, and optional latched-message replay. It is not a ROS2 runtime
or a claim of wire-level ROS compatibility.

## Components

- [`ros_bridge.py`](ros_bridge.py) — `ROS2Bridge`, `TopicMessage`, and `TopicInfo`.

## Validation

Run `uv run pytest tests/unit/embodiment/ -q` from the repository root. Tests
should use local event loops and deterministic payloads.

## Navigation

- [Parent module](../README.md)
- [Parent agent guidance](../AGENTS.md)
