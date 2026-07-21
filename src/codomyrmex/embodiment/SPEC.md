# Embodiment Specification

**Version**: v1.3.0 | **Status**: Active | **Last Updated**: July 2026

## Functional Requirements

- Parse JSON sensor payloads with `node_id`, `timestamp`, `sensor_type`, and `readings`.
- Aggregate telemetry by node and expose the latest payload for each node.
- Serve local WebSocket telemetry ingress and send command JSON to connected nodes.
- Provide simulated sensor and actuator classes with explicit connect/disconnect lifecycles.
- Provide an in-process ROS-style bridge with topic creation, publish, subscribe, latched replay, bounded history, and simulated message delivery.
- Provide `Vec3` vector math and `Transform3D` identity, translation, yaw, compose, inverse, degree/radian, and serialization helpers.

## Non-Functional Requirements

- Runtime behavior is deterministic and local.
- Tests use real local objects and WebSocket connections; no mock transport is needed.
- The module does not claim production ROS2 middleware integration.

## Validation

```bash
uv run pytest tests/unit/embodiment/ -q
uv run ruff check src/codomyrmex/embodiment
uv run ty check --output-format concise src/codomyrmex/embodiment
```

## Navigation

- **README**: [README.md](README.md)
- **Agent Guidance**: [AGENTS.md](AGENTS.md)
- **API Specification**: [API_SPECIFICATION.md](API_SPECIFICATION.md)
- **MCP Tools**: [MCP_TOOL_SPECIFICATION.md](MCP_TOOL_SPECIFICATION.md)
