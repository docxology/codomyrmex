# Actuator Control -- Technical Specification

**Version**: v1.1.0 | **Status**: Active | **Last Updated**: May 2026

## Overview

Actuator control primitives for motor, servo, and gripper interfaces within the embodiment system. The module provides dataclasses and an abstract controller contract for commanding physical or simulated actuators from embodied agents.

## Architecture

This submodule exposes `ActuatorCommand`, `ActuatorStatus`, `ActuatorController`, and a deterministic `SimulatedActuator` implementation. The legacy `MockActuator` name remains as a compatibility alias. Hardware-specific controllers should subclass `ActuatorController`, validate command ranges, and return `ActuatorStatus` snapshots.

## Components

| Component | Purpose |
|-----------|---------|
| `ActuatorCommand` | Dataclass carrying actuator id, command type, parameters, and timestamp |
| `ActuatorStatus` | Dataclass carrying actuator id, status string, feedback, and timestamp |
| `ActuatorController` | Abstract connect/disconnect/execute/status contract |
| `SimulatedActuator` | In-memory deterministic implementation for local runs |
| `MockActuator` | Backward-compatible alias for existing imports |

## Dependencies

- **Internal**: Expected to use `embodiment.transformation` for coordinate transforms
- **External**: Hardware-specific libraries are adapter-specific and not required by the base module

## Constraints

- Base interfaces are synchronous and intentionally small; async fan-out belongs in `embodiment.ros`.
- Zero-mock: hardware adapters should drive real devices; deterministic local behavior uses `SimulatedActuator`.
- Actuator commands must validate range limits before dispatch.

## Error Handling

- Executing while disconnected returns `False` in the simulated implementation.
- Hardware adapters should log device errors before propagation.

## Navigation

- **Self**: `SPEC.md`
- **Parent**: [../README.md](../README.md)
- **Readme**: [README.md](README.md)
- **Agents**: [AGENTS.md](AGENTS.md)
- **Repository Root**: [README.md](../../../../README.md)
