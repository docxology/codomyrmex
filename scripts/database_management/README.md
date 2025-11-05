# Database Management Orchestrator

Thin orchestrator script providing CLI access to the `codomyrmex.database_management` module.

## Purpose

This orchestrator provides command-line interface for database management, backup, and migration operations.

## Usage

```bash
# Backup database
python scripts/database_management/orchestrate.py backup --database mydb --output backup.sql

# Run migrations
python scripts/database_management/orchestrate.py migrate --database mydb
```

## Commands

- `backup` - Backup database
- `migrate` - Run database migrations

## Related Documentation

- **[Module README](../../src/codomyrmex/database_management/README.md)**: Complete module documentation
- **[CLI Reference](../../docs/reference/cli.md)**: Main CLI documentation

## Integration

This orchestrator calls functions from:
- `codomyrmex.database_management.backup_database`
- `codomyrmex.database_management.run_migrations`

See `codomyrmex.cli.py` for main CLI integration.

