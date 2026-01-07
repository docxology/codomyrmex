# config/database

## Signposting
- **Parent**: [config](../README.md)
- **Children**:
    - [examples](examples/README.md)
- **Key Artifacts**:
    - [Agent Guide](AGENTS.md)
    - [Functional Spec](SPEC.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Overview

Database connection and configuration templates for Codomyrmex. Provides centralized configuration for database connections, connection pools, migration settings, and backup configurations used across multiple modules.

## Directory Contents

- `README.md` – This file
- `SPEC.md` – Functional specification
- `AGENTS.md` – Agent coordination documentation
- `connections.yaml` – Database connection templates
- `pools.yaml` – Connection pool configurations
- `migrations.yaml` – Migration settings
- `backups.yaml` – Backup configurations
- `examples/` – Example database configs (SQLite, PostgreSQL, Redis, MongoDB)

## Configuration Files

### connections.yaml
Database connection templates for different database types (SQLite, PostgreSQL, MySQL, MongoDB, Redis). Defines connection parameters, SSL settings, and connection strings.

### pools.yaml
Connection pool configurations including pool size, timeout settings, and retry policies.

### migrations.yaml
Migration settings including migration directory, naming patterns, auto-rollback, and timeout configurations.

### backups.yaml
Backup configurations including backup directory, naming patterns, compression, retention policies, and encryption settings.

## Supported Database Types

- **SQLite** - File-based database for development and testing
- **PostgreSQL** - Production relational database
- **MySQL** - Alternative relational database
- **MongoDB** - Document database
- **Redis** - In-memory data store and cache

## Usage

Database configurations are loaded by the `config_management` module and used by:
- `database_management/` - Database operations and migrations
- `project_orchestration/` - Workflow and project data storage
- `cache/` - Redis cache backend
- `events/` - Event storage

## Best Practices

- Use environment variables for database credentials
- Configure connection pools appropriately for your workload
- Enable SSL/TLS for production databases
- Set up regular backups with retention policies
- Monitor database connections and performance

## Navigation

- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Examples**: [examples/](examples/README.md)
- **Parent Directory**: [config](../README.md)
- **Project Root**: [README](../../README.md)

