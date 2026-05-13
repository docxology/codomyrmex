# Sensor Interfaces -- Technical Specification

**Version**: v1.1.0 | **Status**: Active | **Last Updated**: May 2026

## Overview

Sensor interface primitives for the embodiment system. The submodule provides a hardware-abstraction layer for reading sensor data from embodied agents and feeding it into perception or ROS bridge pipelines.

## Architecture

This submodule exposes `SensorData`, `SensorInterface`, and a deterministic `SimulatedSensor` implementation. The legacy `MockSensor` name remains as a compatibility alias for callers that imported the earlier class. Concrete hardware integrations should subclass `SensorInterface` and return timestamped `SensorData` objects.

## Components

| Component | Purpose |
|-----------|---------|
| `SensorData` | Dataclass carrying `sensor_id`, timestamp, metadata, and payload |
| `SensorInterface` | Abstract connect/disconnect/read contract for sensor adapters |
| `SimulatedSensor` | In-memory deterministic implementation for local runs |
| `MockSensor` | Backward-compatible alias preserving legacy metadata |

## Dependencies

- **Internal**: Can publish sensor data via `embodiment.ros.ROS2Bridge` topics
- **External**: Hardware-specific libraries are adapter-specific and not required by the base module

## Constraints

- Base interfaces are synchronous and intentionally small; async fan-out belongs in `embodiment.ros`.
- Zero-mock: hardware adapters should read real devices; deterministic local behavior uses `SimulatedSensor`.
- Sensor readings must include timestamps for temporal alignment.

## Error Handling

- Reading before `connect()` raises `RuntimeError`.
- Hardware adapters should log device errors before propagation.

## Navigation

- **Self**: `SPEC.md`
- **Parent**: [../README.md](../README.md)
- **Readme**: [README.md](README.md)
- **Agents**: [AGENTS.md](AGENTS.md)
- **Repository Root**: [README.md](../../../../README.md)
