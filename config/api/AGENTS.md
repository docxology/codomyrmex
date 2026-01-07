# Codomyrmex Agents — config/api

## Signposting
- **Parent**: [config](../AGENTS.md)
- **Self**: [api Agents](AGENTS.md)
- **Children**:
    - [examples](examples/AGENTS.md)
- **Key Artifacts**:
    - [Functional Spec](SPEC.md)
    - [Human Readme](README.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose

API and service configuration templates for API endpoints, service URLs, API versions, and rate limiting. Used across `api/`, `networking/`, and `project_orchestration/` modules.

## Active Components

- `README.md` – API configuration documentation
- `SPEC.md` – Functional specification
- `endpoints.yaml` – API endpoint definitions
- `rate-limiting.yaml` – Rate limiting configurations
- `versions.yaml` – API versioning configurations
- `examples/` – Example API configs

## Operating Contracts

- Maintain alignment between code, documentation, and API configurations.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.

## Navigation Links

- **Human Documentation**: [README.md](README.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Examples**: [examples/](examples/README.md)
- **Parent**: [config](../AGENTS.md)
- **Project Root**: [README](../../README.md)

