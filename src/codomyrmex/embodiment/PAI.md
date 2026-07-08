# Personal AI Infrastructure - Embodiment Module

**Version**: v1.3.0 | **Status**: Active | **Last Updated**: July 2026

## Overview

The embodiment module provides deterministic local interfaces for simulated
hardware and robotics-adjacent workflows: telemetry parsing, WebSocket ingress,
actuator commands, ROS-style pub/sub, and 3D transforms. PAI uses it as a safe
testbed for embodied-agent planning without requiring physical devices.

## PAI Capabilities

| Capability | Purpose |
| :--- | :--- |
| Telemetry streams | Normalize sensor payloads and retain latest readings by node |
| Simulated sensors | Produce deterministic sensor readings for tests and demos |
| Simulated actuators | Validate actuator command lifecycle without hardware side effects |
| WebSocket bridge | Accept local telemetry and queue outbound actuator commands |
| ROS-style bridge | Exercise topic publish/subscribe flows in process |
| Transform math | Compose, invert, and apply local 3D transforms |

## Key Exports

| Export | Type | Purpose |
| :--- | :--- | :--- |
| `SensorPayload` | Class | Structured sensor reading |
| `TelemetryStream` | Class | Latest-reading registry |
| `EmbodimentBridge` | Class | WebSocket telemetry and command bridge |
| `SimulatedSensor` | Class | Deterministic sensor source |
| `SimulatedActuator` | Class | Deterministic actuator sink |
| `ROS2Bridge` | Class | In-process topic bridge |
| `Vec3` | Class | 3D vector value |
| `Transform3D` | Class | Euler transform composition and inversion |

## PAI Algorithm Phase Mapping

| Phase | Embodiment Contribution |
| :--- | :--- |
| **OBSERVE** | Parse sensor payloads and maintain latest telemetry state |
| **PLAN** | Represent spatial transforms and topic-level embodied context |
| **BUILD** | Exercise bridge and actuator logic in a local simulation harness |
| **VERIFY** | Validate deterministic command lifecycle and pub/sub behavior |
| **LEARN** | Retain simulated traces that can inform future embodied policies |

## MCP Integration

The module currently has no exported MCP tools. It is consumed programmatically
by tests, demos, and higher-level agent orchestration code that needs a
zero-hardware embodiment surface.

## Navigation

- **Self**: [PAI.md](PAI.md)
- **Module README**: [README.md](README.md)
- **Specification**: [SPEC.md](SPEC.md)
- **API Specification**: [API_SPECIFICATION.md](API_SPECIFICATION.md)
- **MCP Tool Specification**: [MCP_TOOL_SPECIFICATION.md](MCP_TOOL_SPECIFICATION.md)
