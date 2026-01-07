# database_management

## Signposting
- **Parent**: [codomyrmex](../README.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [Agent Guide](AGENTS.md)
    - [Functional Spec](SPEC.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Overview

Database operations including database connection management, query execution, schema management, migration handling, backup and restore, and performance monitoring. Provides unified interface for database operations across different database backends.

## Directory Contents
- `API_SPECIFICATION.md` – File
- `README.md` – File
- `SECURITY.md` – File
- `SPEC.md` – File
- `__init__.py` – File
- `backup_manager.py` – File
- `db_manager.py` – File
- `migration_manager.py` – File
- `performance_monitor.py` – File
- `schema_generator.py` – File

## Navigation
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: [README](../../../README.md)

## Getting Started

To use this module in your project, import the necessary components:

```python
from codomyrmex.database_management import (
    DatabaseManager,
    MigrationManager,
    BackupManager,
    SchemaGenerator,
)

# Connect to database
db = DatabaseManager()
db.connect(connection_string="postgresql://user:pass@localhost/db")

# Run migrations
migration = MigrationManager()
migration.run_migrations("migrations/")

# Create backup
backup = BackupManager()
backup.create_backup("backup_20250101.sql")

# Generate schema
schema_gen = SchemaGenerator()
schema = schema_gen.generate_from_models(models=["User", "Post"])
db.apply_schema(schema)

# Execute query
results = db.execute_query("SELECT * FROM users WHERE active = %s", (True,))
```

