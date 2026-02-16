# Migration Module

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Provider and data migration tools for schema changes and data transformations. Supports defining multi-step migrations with up/down (rollback) functions, running them in sequence with status tracking, and transforming data records through composable field-level transformers for renaming, type conversion, and custom logic.

## Installation

```bash
uv add codomyrmex
```

Or for development:

```bash
uv sync
```

## Key Exports

### Enums

- **`MigrationStatus`** -- Status of a migration: PENDING, RUNNING, COMPLETED, FAILED, ROLLED_BACK
- **`MigrationDirection`** -- Direction of execution: UP (forward) or DOWN (rollback)

### Data Classes

- **`MigrationStep`** -- A single migration step with ID, name, optional up/down callable functions, and dependency declarations
- **`MigrationResult`** -- Result of a migration run with status, step progress tracking, duration, and error details; includes `progress` percentage and `duration_seconds` properties
- **`Migration`** -- A complete migration definition with ID, name, version, and ordered list of steps; supports fluent `add_step()` and `add_simple_step()` builders

### Transformers

- **`DataTransformer`** -- Abstract base class for data transformation with a single `transform()` method
- **`FieldRenameTransformer`** -- Renames dictionary keys according to a provided mapping
- **`FieldTypeTransformer`** -- Converts dictionary field values to specified Python types (e.g., str to int)
- **`CompositeTransformer`** -- Chains multiple transformers to apply in sequence

### Services

- **`MigrationRunner`** -- Executes migrations in forward or rollback direction; tracks completed migrations, supports `rollback()` shorthand, and provides `is_completed()` status checks
- **`DataMigrator`** -- Migrates lists of data records through a chain of transformers; supports both batch `migrate()` and single-record `migrate_single()` operations

## Directory Contents

- `models.py` -- Data models (Migration, MigrationStep, MigrationResult)
- `runner.py` -- Migration runner logic (MigrationRunner, DataMigrator)
- `transformers.py` -- Data transformers
- `__init__.py` -- Public API re-exports
- `README.md` -- This file
- `AGENTS.md` -- Agent integration documentation
- `API_SPECIFICATION.md` -- Programmatic API specification
- `MCP_TOOL_SPECIFICATION.md` -- Model Context Protocol tool definitions
- `PAI.md` -- PAI integration notes
- `SPEC.md` -- Module specification
- `py.typed` -- PEP 561 type stub marker

## Quick Start

```python
from codomyrmex.migration import MigrationStatus, MigrationDirection, MigrationStep

# Initialize MigrationStatus
instance = MigrationStatus()
```

## Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k migration -v
```

## Navigation

- **Full Documentation**: [docs/modules/migration/](../../../docs/modules/migration/)
- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: ../../../README.md
