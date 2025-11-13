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
- Database connections maintain security and connection pooling efficiency.
- Migration management ensures data integrity and supports rollback capabilities.

## Related Modules
- **Project Orchestration** (`project_orchestration/`) - Uses database for workflow state management
- **Logging Monitoring** (`logging_monitoring/`) - Stores logs in database backends
- **Config Management** (`config_management/`) - Manages database configuration settings

## Navigation Links
- **📚 Module Overview**: [README.md](README.md) - Module documentation and usage
- **🔒 Security**: [SECURITY.md](SECURITY.md) - Security considerations
- **🏠 Package Root**: [../../README.md](../../README.md) - Package overview
- **📖 Documentation Hub**: [../../../docs/README.md](../../../docs/README.md) - Complete documentation
