# Backup — Agent Coordination

## Purpose

Provides database backup and restore capabilities for AI agents managing data persistence across SQLite, PostgreSQL, and MySQL databases, with compression, checksums, and manifest-based tracking.

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `backup.py` | `DatabaseBackup` | SQLite file-copy and PostgreSQL `pg_dump` backup/restore with manifest tracking |
| `backup.py` | `BackupMetadata` | Dataclass capturing timestamp, database name, format, size, and file path |
| `backup.py` | `BackupFormat` | Enum for backup output formats (`SQL`, `CUSTOM`, `DIRECTORY`, `TAR`) |
| `backup_manager.py` | `BackupManager` | Full-featured backup manager supporting SQLite/PostgreSQL/MySQL with gzip compression and SHA256 checksums |
| `backup_manager.py` | `Backup` | Dataclass storing backup ID, database URL, file path, timestamp, size, and checksum |
| `backup_manager.py` | `BackupResult` | Dataclass wrapping success status, backup reference, duration, and error message |
| `backup_manager.py` | `backup_database` | Convenience function for single-call backup creation |

## Operating Contracts

- Agents MUST provide valid filesystem paths for `backup_dir`; directories are created automatically if absent.
- `DatabaseBackup` writes a `backup_manifest.json` file alongside backups for tracking; agents should not modify this file directly.
- `BackupManager` generates SHA256 checksums for every backup and stores them in the `Backup` dataclass; agents can use these to verify integrity.
- PostgreSQL backups require `pg_dump` / `psql` available on `PATH`.
- MySQL backups in `BackupManager` require `pymysql` installed.
- The `prune` method on `DatabaseBackup` removes backups older than `max_age_days` and enforces `max_backups` count.
- `BackupManager.restore` only supports SQLite restoration (reads SQL from gzip and executes).

## Integration Points

- **logging_monitoring**: `BackupManager` uses the codomyrmex structured logger for operation logging.
- **exceptions**: `BackupManager` raises `CodomyrmexError` on failures.
- **orchestrator**: Backup tasks can be scheduled as workflow steps via the orchestrator module.

## Navigation

- **Parent**: [database_management/README.md](../README.md)
- **Siblings**: [lineage/](../lineage/), [migration/](../migration/)
- **RASP**: [README.md](README.md) | **AGENTS.md** | [SPEC.md](SPEC.md) | [PAI.md](PAI.md)
