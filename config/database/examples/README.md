# config/database/examples

## Signposting
- **Parent**: [config/database](../README.md)
- **Key Artifacts**:
    - [Agent Guide](AGENTS.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Overview

Example database configurations demonstrating best practices for different database types including SQLite, PostgreSQL, MySQL, MongoDB, and Redis.

## Example Files

- `sqlite-example.yaml` – Example SQLite configuration for development
- `postgresql-example.yaml` – Example PostgreSQL configuration for production
- `redis-example.yaml` – Example Redis configuration for caching
- `mongodb-example.yaml` – Example MongoDB configuration for document storage

## Usage

These examples can be used as starting points for configuring databases in your Codomyrmex deployment. Copy and customize the examples as needed, ensuring all credentials use environment variables.

## Best Practices

- Use environment variables for database credentials
- Configure connection pools appropriately
- Enable SSL/TLS for production databases
- Set up regular backups with retention policies
- Monitor database connections and performance

## Navigation

- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Parent Directory**: [config/database](../README.md)
- **Project Root**: [README](../../../README.md)

