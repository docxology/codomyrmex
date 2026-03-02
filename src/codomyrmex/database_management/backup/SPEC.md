# Backup — Functional Specification

## Overview

The backup submodule provides two complementary backup systems for database persistence: `DatabaseBackup` for direct SQLite/PostgreSQL operations with manifest tracking, and `BackupManager` for a higher-level interface with compression, checksums, and multi-database support.

## Architecture

```
backup/
  backup.py          -- DatabaseBackup, BackupMetadata, BackupFormat
  backup_manager.py  -- BackupManager, Backup, BackupResult, backup_database
  __init__.py         -- Re-exports from both modules
```

Two independent class hierarchies coexist:

- **DatabaseBackup** (backup.py): Direct filesystem operations, JSON manifest, no compression.
- **BackupManager** (backup_manager.py): URL-based connection parsing, gzip compression, SHA256 verification.

## Key Classes

### DatabaseBackup

| Method | Signature | Behaviour |
|--------|-----------|-----------|
| `__init__` | `(backup_dir: str)` | Creates backup directory if absent; loads manifest from `backup_manifest.json` |
| `backup_sqlite` | `(db_path: str, backup_name: str) -> BackupMetadata` | Copies SQLite file to backup dir, records in manifest |
| `restore_sqlite` | `(backup_name: str, restore_path: str) -> bool` | Restores from manifest entry, copies backup file to target path |
| `backup_postgres` | `(connection_string: str, backup_name: str, format: BackupFormat) -> BackupMetadata` | Runs `pg_dump` via subprocess with specified format flag |
| `list_backups` | `() -> list[BackupMetadata]` | Returns all tracked backups from manifest |
| `prune` | `(max_age_days: int, max_backups: int) -> int` | Removes expired/excess backups from disk and manifest; returns count removed |

### BackupManager

| Method | Signature | Behaviour |
|--------|-----------|-----------|
| `__init__` | `(backup_dir: str)` | Creates backup directory; initialises empty backup list |
| `create_backup` | `(database_url: str) -> BackupResult` | Parses URL scheme, dispatches to `_backup_sqlite`/`_backup_postgres`/`_backup_mysql`, compresses with gzip, computes SHA256 |
| `restore` | `(backup_id: str, target_url: str) -> BackupResult` | Currently supports SQLite only; decompresses gzip, executes SQL statements |
| `list_backups` | `() -> list[Backup]` | Returns all tracked `Backup` instances |
| `get_backup` | `(backup_id: str) -> Backup \| None` | Looks up backup by ID |

### BackupFormat (Enum)

| Member | Value | Used by |
|--------|-------|---------|
| `SQL` | `"sql"` | `pg_dump --format=plain` |
| `CUSTOM` | `"custom"` | `pg_dump --format=custom` |
| `DIRECTORY` | `"directory"` | `pg_dump --format=directory` |
| `TAR` | `"tar"` | `pg_dump --format=tar` |

## Data Models

### BackupMetadata

Fields: `name` (str), `timestamp` (str), `database_name` (str), `format` (str), `size_bytes` (int), `file_path` (str).

### Backup

Fields: `id` (str, UUID4), `database_url` (str), `file_path` (str), `timestamp` (datetime), `size_bytes` (int), `checksum` (str, SHA256).

### BackupResult

Fields: `success` (bool), `backup` (Backup | None), `duration_seconds` (float), `error` (str | None).

## Dependencies

- **Standard library**: `shutil`, `subprocess`, `gzip`, `hashlib`, `uuid`, `json`, `urllib.parse`
- **Internal**: `codomyrmex.exceptions.CodomyrmexError`, `codomyrmex.logging_monitoring`
- **Optional external**: `psycopg2` (PostgreSQL via BackupManager), `pymysql` (MySQL via BackupManager)

## Constraints

- `DatabaseBackup.backup_postgres` requires `pg_dump` on the system PATH; failure raises `RuntimeError`.
- `BackupManager.restore` only implements SQLite restoration; PostgreSQL and MySQL restore raise `NotImplementedError`.
- Manifest file (`backup_manifest.json`) uses simple JSON serialization; concurrent writes are not synchronized.
- Gzip compression in `BackupManager` uses default compression level.

## Error Handling

- `BackupManager` wraps failures in `BackupResult(success=False, error=str(e))` and logs via structured logger.
- `DatabaseBackup` raises `FileNotFoundError` for missing source files and `RuntimeError` for subprocess failures.
- Missing optional database drivers (`psycopg2`, `pymysql`) cause `ImportError` at call time, not at import time.
