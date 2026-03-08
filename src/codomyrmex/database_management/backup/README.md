# Database Backup

**Version**: v1.1.9 | **Updated**: March 2026

## Overview

The `database_management.backup` submodule provides automated database backup, restore, and pruning for SQLite, PostgreSQL, and MySQL databases. Two complementary systems are offered:

- **`DatabaseBackup`** (backup.py): Direct file-copy and `pg_dump` operations with JSON manifest tracking.
- **`BackupManager`** (backup_manager.py): Higher-level interface with URL-based connection parsing, gzip compression, SHA256 checksums, and multi-database support.

## PAI Integration

| Phase | Tool / Class | Usage |
|-------|-------------|-------|
| EXECUTE | `DatabaseBackup.backup_sqlite` | File-copy backup of SQLite databases |
| EXECUTE | `DatabaseBackup.backup_postgres` | `pg_dump` backup of PostgreSQL databases |
| EXECUTE | `BackupManager.create_backup` | URL-routed backup with compression and checksums |
| VERIFY | `BackupManager._calculate_checksum` | SHA256 integrity verification |
| EXECUTE | `DatabaseBackup.restore_sqlite` | Restore SQLite from manifest-tracked backup |

## Key Exports

| Export | Type | Description |
|--------|------|-------------|
| `DatabaseBackup` | Class | SQLite/PostgreSQL backup and restore with manifest tracking |
| `BackupMetadata` | Dataclass | Metadata for a single backup (ID, source, destination, format, timestamp, size, checksum) |
| `BackupFormat` | Enum | Supported formats: `SQL_DUMP`, `FILE_COPY`, `COMPRESSED` |
| `BackupManager` | Class | Full-featured backup manager with URL parsing, gzip, SHA256 |
| `Backup` | Dataclass | Backup record with ID, database name, type, path, size, compression, checksum |
| `BackupResult` | Dataclass | Operation result with success status, duration, file size, errors, warnings |
| `backup_database` | Function | Convenience function for single-call backup creation |

## Quick Start

### SQLite backup with DatabaseBackup

```python
from pathlib import Path
from codomyrmex.database_management.backup import DatabaseBackup

db_backup = DatabaseBackup(backup_dir=Path("/tmp/backups"))
metadata = db_backup.backup_sqlite(
    db_path=Path("my_database.db"),
    backup_name="daily_backup"
)
print(f"Backup saved: {metadata.destination} ({metadata.size_bytes} bytes)")

# Restore
db_backup.restore_sqlite("daily_backup", Path("restored.db"))

# List and prune
all_backups = db_backup.list_backups()
removed = db_backup.prune(keep_last=5)
```

### Multi-database backup with BackupManager

```python
from codomyrmex.database_management.backup import BackupManager

manager = BackupManager(workspace_dir="/tmp/workspace")
result = manager.create_backup(
    database_name="myapp",
    database_url="sqlite:///data/app.db",
    compression="gzip",
)
print(f"Success: {result.success}, Size: {result.file_size_mb:.2f} MB")
print(f"Checksum: {result.checksum}")
```

### Convenience function

```python
from codomyrmex.database_management.backup import backup_database

result = backup_database("myapp", database_url="sqlite:///data/app.db")
```

## Architecture

```
backup/
  __init__.py          -- Re-exports from backup.py and backup_manager.py
  backup.py            -- DatabaseBackup, BackupMetadata, BackupFormat
  backup_manager.py    -- BackupManager, Backup, BackupResult, backup_database
```

## MCP Tools

This submodule does not expose MCP tools. Backup operations are accessed programmatically.

## Testing

```bash
uv run pytest src/codomyrmex/tests/unit/database_management/ -v
```

PostgreSQL tests require `pg_dump` on PATH and are gated with `@pytest.mark.skipif`. MySQL tests require `mysqldump` on PATH.

## Navigation

- **Parent**: [database_management/README.md](../README.md)
- **Siblings**: [lineage/](../lineage/), [migration/](../migration/)
- **RASP**: **README.md** | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md)
