# Codomyrmex Agents — config/database

## Signposting
- **Parent**: [config](../AGENTS.md)
- **Self**: [database Agents](AGENTS.md)
- **Children**:
    - [examples](examples/AGENTS.md)
- **Key Artifacts**:
    - [Functional Spec](SPEC.md)
    - [Human Readme](README.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose

Database connection and configuration templates for database connections, connection pools, migration settings, and backup configurations. Used across `database_management/`, `project_orchestration/`, `cache/` (Redis), and `events/` modules.

## Active Components

- `README.md` – Database configuration documentation
- `SPEC.md` – Functional specification
- `connections.yaml` – Database connection templates
- `pools.yaml` – Connection pool configurations
- `migrations.yaml` – Migration settings
- `backups.yaml` – Backup configurations
- `examples/` – Example database configs (SQLite, PostgreSQL, Redis, MongoDB)

## Operating Contracts

- Maintain alignment between code, documentation, and database configurations.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.
- Use environment variable references for database credentials.
- Support multiple database types (SQLite, PostgreSQL, MySQL, MongoDB, Redis).

## Navigation Links

- **Human Documentation**: [README.md](README.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Examples**: [examples/](examples/README.md)
- **Parent**: [config](../AGENTS.md)
- **Project Root**: [README](../../README.md)

