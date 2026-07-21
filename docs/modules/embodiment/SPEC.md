# embodiment - Functional Specification

**Version**: v1.3.0 | **Status**: Active | **Last Updated**: July 2026

## Purpose

Provide safe, deterministic local embodiment surfaces for tests, demos, and
agent workflows that need simulated telemetry or actuator behavior.

## Functional Requirements

1. Parse structured sensor payloads and retain latest readings by node.
2. Provide deterministic simulated sensors and actuators.
3. Accept local WebSocket telemetry and queue outbound actuator commands.
4. Provide in-process ROS-style topic publish/subscribe and history behavior.
5. Compose, invert, and apply 3D transforms without external services.

## Interface Contracts

```python
from codomyrmex.embodiment import EmbodimentBridge, SimulatedSensor, Transform3D

sensor = SimulatedSensor("temperature", value=21.5)
reading = sensor.read()

bridge = EmbodimentBridge()
transform = Transform3D.identity()
```

## Validation

```bash
uv run pytest tests/unit/embodiment/ -q
uv run ruff check src/codomyrmex/embodiment
uv run ty check --output-format concise src/codomyrmex/embodiment
```

## Navigation

- **Module Overview**: [README.md](README.md)
- **Agent Guidance**: [AGENTS.md](AGENTS.md)
- **API Specification**: [API_SPECIFICATION.md](API_SPECIFICATION.md)
- **PAI Mapping**: [PAI.md](PAI.md)
