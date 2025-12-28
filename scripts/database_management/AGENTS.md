# Codomyrmex Agents — scripts/database_management

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: December 2025

## Purpose

Database management automation scripts providing command-line interfaces for database backup, migration, and maintenance operations. This script module enables automated database workflows for Codomyrmex projects.

The database_management scripts serve as the primary interface for database administrators and developers to manage database operations and maintenance tasks.

## Module Overview

### Key Capabilities
- **Database Backup**: Create and manage database backups
- **Database Migration**: Execute schema migrations and data transformations
- **Database Maintenance**: Perform optimization and maintenance operations
- **Multi-Database Support**: Support for different database types and providers
- **Security Handling**: Secure credential management for database access

### Key Features
- Command-line interface with argument parsing
- Integration with core database management modules
- Structured output formatting (JSON, text, verbose)
- Error handling and validation
- Logging integration for database operations tracking

## Function Signatures

### Core CLI Functions

```python
def main() -> None
```

Main CLI entry point for the database management orchestrator.

**Command-line Usage:**
```bash
python orchestrate.py [command] [options]
```

**Available Commands:**
- `backup` - Create database backups
- `migrate` - Execute database migrations

**Global Options:**
- `--verbose, -v` - Enable verbose output
- `--database-url, -d` - Database connection URL

```python
def handle_backup(args) -> None
```

Handle database backup commands from CLI arguments.

**Parameters:**
- `args` - Parsed command-line arguments containing:
  - `database_url` (str): Database connection URL
  - `backup_path` (str, optional): Path to save backup file
  - `backup_type` (str, optional): Type of backup ("full", "incremental", "schema"). Defaults to "full"
  - `compression` (str, optional): Compression format ("gzip", "bz2", "none"). Defaults to "gzip"
  - `include_data` (bool, optional): Include data in backup. Defaults to True
  - `exclude_tables` (list, optional): List of tables to exclude from backup

**Returns:** None (creates database backup and outputs results)

```python
def handle_migrate(args) -> None
```

Handle database migration commands from CLI arguments.

**Parameters:**
- `args` - Parsed command-line arguments containing:
  - `database_url` (str): Database connection URL
  - `migration_path` (str): Path to migration files or directory
  - `target_version` (str, optional): Target migration version
  - `dry_run` (bool, optional): Execute migration in dry-run mode. Defaults to False
  - `rollback` (bool, optional): Rollback to previous version. Defaults to False
  - `force` (bool, optional): Force migration even with potential data loss. Defaults to False

**Returns:** None (executes database migration and outputs results)

## Active Components

### Core Implementation
- `__init__.py` – Module initialization and public API exports
- `orchestrate.py` – Main CLI orchestrator script

### Documentation
- `README.md` – Script usage and overview
- `AGENTS.md` – This coordination document

### Supporting Files
- Integration with `_orchestrator_utils.py` for shared utilities

## Operating Contracts

### Universal Script Protocols

All scripts in this module must:

1. **CLI Standards**: Follow consistent command-line argument patterns
2. **Error Handling**: Provide clear error messages and exit codes
3. **Logging Integration**: Use centralized logging for all operations
4. **Security**: Handle database credentials securely
5. **Data Safety**: Ensure backup and migration operations are safe

### Module-Specific Guidelines

#### Database Backup
- Validate database connectivity before backup operations
- Provide progress feedback for large database backups
- Support different backup formats and compression options
- Handle backup encryption for sensitive data

#### Database Migration
- Validate migration scripts before execution
- Support transactional migrations with rollback capability
- Provide migration history and version tracking
- Handle schema changes safely with data preservation

#### Database Maintenance
- Perform maintenance operations during low-usage periods
- Provide detailed logging of maintenance activities
- Support automated scheduling of maintenance tasks
- Monitor database performance metrics

## Navigation Links

### Module Documentation
- **Script Overview**: [README.md](README.md) - Complete script documentation

### Related Scripts

### Platform Navigation
- **Scripts Directory**: [../README.md](../README.md) - Scripts directory overview

## Agent Coordination

### Integration Points

When integrating with other scripts:

1. **Shared Utilities**: Use `_orchestrator_utils.py` for common CLI patterns
2. **Backup Coordination**: Share backup files with other maintenance scripts
3. **Migration Integration**: Coordinate schema changes with application deployments
4. **Security Coordination**: Share secure credential handling patterns

### Quality Gates

Before script changes are accepted:

1. **CLI Testing**: All command-line options work correctly
2. **Database Testing**: Scripts work with various database types and configurations
3. **Backup Testing**: Backup operations produce valid and restorable backups
4. **Migration Testing**: Migration operations work correctly and safely
5. **Integration Testing**: Scripts work with core database management modules

## Version History

- **v0.1.0** (December 2025) - Initial database management automation scripts with backup and migration capabilities
