# Codomyrmex Agents — src/codomyrmex/database_management

## Purpose
Database management agents providing unified interface for multiple database systems, supporting connection pooling, query optimization, and migration management across different database backends.

## Active Components
- `db_manager.py` – Unified database management interface supporting multiple database backends (PostgreSQL, MySQL, SQLite) with connection pooling and query optimization
- `__init__.py` – Package initialization and database connector exports

## Operating Contracts
- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.

## Checkpoints
- [ ] Confirm AGENTS.md reflects the current module purpose.
- [ ] Verify logging and telemetry hooks for this directory's agents.
- [ ] Sync automation scripts or TODO entries after modifications.
