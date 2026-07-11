# Embodiment -- Technical Specification

**Version**: v1.1.9 | **Status**: Active | **Last Updated**: March 2026

## Functional Requirements

- Parse JSON sensor payloads and reject invalid payloads with `ValueError`.
- Track latest telemetry per node.
- Accept local WebSocket telemetry and send command JSON to connected nodes.
- Provide simulated sensor and actuator lifecycles.
- Provide an in-process ROS-style topic bridge with bounded history, latching, and simulated message delivery.
- Provide `Vec3` and `Transform3D` vector and Euler-transform helpers.

## Non-Functional Requirements

- Tests use real local objects and WebSocket transport where available.
- The module is a local compatibility surface and does not claim production ROS2 middleware integration.
- Runtime behavior should stay deterministic and dependency-light.

## Navigation

- **Source**: [../../../../embodiment/README.md](../../../../embodiment/README.md)
- **Extended README**: [README.md](readme.md)
- **AGENTS**: [AGENTS.md](AGENTS.md)
- **Parent**: [All Modules](../README.md)
## Maintenance Notes

- Keep this document synchronized with adjacent source files.
- Update sibling README, AGENTS, and SPEC documents together.
- Preserve working examples when changing public behavior.
- Prefer measured validation output over inferred status claims.
- Record any remaining gaps in TODO.md or the nearest planning document.
