# embodiment

**Version**: v1.3.0 | **Status**: Active | **Last Updated**: July 2026

## Overview

The embodiment module provides local simulated hardware interfaces used by tests
and demos: telemetry parsing, a WebSocket bridge, simulated sensors and
actuators, an in-process ROS-style pub/sub bridge, and 3D vector transforms.

## Key Components

| Component | File | Purpose |
| :--- | :--- | :--- |
| `SensorPayload` / `TelemetryStream` | `telemetry.py` | Parse and retain latest sensor readings by node |
| `EmbodimentBridge` | `bridge.py` | WebSocket telemetry ingress and actuator command egress |
| `SimulatedSensor` / `MockSensor` | `sensors/base.py` | Deterministic sensor readings |
| `SimulatedActuator` / `MockActuator` | `actuators/base.py` | Deterministic actuator command lifecycle |
| `ROS2Bridge` | `ros/ros_bridge.py` | In-process topic history, latching, subscribe, publish, and simulation |
| `Vec3` / `Transform3D` | `transformation/transformation.py` | Vector math and Euler transform composition |

## Validation

```bash
uv run pytest src/codomyrmex/tests/unit/embodiment/ -q
uv run ruff check src/codomyrmex/embodiment
uv run ty check --output-format concise src/codomyrmex/embodiment
```

## Navigation

- **Agent Guidance**: [AGENTS.md](AGENTS.md)
- **Specification**: [SPEC.md](SPEC.md)
- **API Specification**: [API_SPECIFICATION.md](API_SPECIFICATION.md)
- **MCP Tools**: [MCP_TOOL_SPECIFICATION.md](MCP_TOOL_SPECIFICATION.md)
