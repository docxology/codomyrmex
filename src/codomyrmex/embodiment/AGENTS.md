# Codomyrmex Agents - src/codomyrmex/embodiment

**Version**: v1.3.0 | **Status**: Active | **Last Updated**: July 2026

## Purpose

Local simulated embodiment package for telemetry parsing, WebSocket hardware
bridging, simulated sensors and actuators, ROS-style pub/sub, and 3D transforms.

## Active Components

- `bridge.py` - WebSocket telemetry ingress and command egress.
- `telemetry.py` - SensorPayload parsing and TelemetryStream aggregation.
- `sensors/base.py` - SensorData, SimulatedSensor, and MockSensor.
- `actuators/base.py` - ActuatorCommand, ActuatorStatus, SimulatedActuator, and MockActuator.
- `ros/ros_bridge.py` - In-process ROS2Bridge compatibility surface.
- `transformation/transformation.py` - Vec3 and Transform3D math.
- `README.md` - Module overview.
- `SPEC.md` - Functional and validation contract.

## Operating Contracts

- Preserve the import paths exercised by `tests/unit/embodiment/`.
- Keep WebSocket tests real and local; do not replace them with mocks.
- Keep transform math deterministic and dependency-light.
- Do not claim production ROS2 integration; this package is an in-process compatibility surface.

## Key Files

- `AGENTS.md` - Agent coordination and navigation.
- `README.md` - User-facing module overview.
- `SPEC.md` - Module behavior contract.
- `API_SPECIFICATION.md` - Python API reference.
- `MCP_TOOL_SPECIFICATION.md` - MCP tool status.
- `bridge.py`
- `telemetry.py`
- `actuators/base.py`
- `sensors/base.py`
- `ros/ros_bridge.py`
- `transformation/transformation.py`

## Dependencies

- Uses Python standard library modules.
- WebSocket bridge tests use the project `websockets` dependency when available.

## Development Guidelines

- Keep interfaces small and deterministic.
- Add zero-mock tests for new simulated hardware behavior.
- Update docs when method signatures or return shapes change.

## Navigation Links

- **Module Overview**: [README.md](README.md)
- **Specification**: [SPEC.md](SPEC.md)
- **Parent Package**: [../README.md](../README.md)
