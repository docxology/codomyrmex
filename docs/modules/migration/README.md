# Migration Module Documentation

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The Migration module provides provider and data migration tools for Codomyrmex. It supports step-based schema/infrastructure migrations with up/down (rollback) semantics, as well as data migrations with pluggable transformation pipelines. The module tracks migration status, progress, and duration, and provides composable data transformers for field renaming, type conversion, and custom transformations.

## Key Features

- **Step-Based Migrations**: Define migrations as ordered sequences of steps with `up` (apply) and `down` (rollback) functions
- **Migration Runner**: Execute migrations forward or roll them back, with per-step success tracking and failure handling
- **Migration Status Tracking**: Track status (PENDING, RUNNING, COMPLETED, FAILED, ROLLED_BACK), progress percentage, and duration
- **Data Transformation Pipeline**: Composable transformer chain for migrating data records
- **Field Rename Transformer**: Rename dictionary keys according to a mapping
- **Field Type Transformer**: Convert field values to target types with error tolerance
- **Composite Transformer**: Chain multiple transformers in sequence for complex migrations
- **Data Migrator**: High-level data migration with batch and single-record support

## Key Components

| Component | Description |
|-----------|-------------|
| `MigrationStatus` | Enum of migration states: PENDING, RUNNING, COMPLETED, FAILED, ROLLED_BACK |
| `MigrationDirection` | Enum for migration direction: UP (apply) or DOWN (rollback) |
| `MigrationStep` | A single migration step with ID, name, up/down functions, and dependency tracking |
| `MigrationResult` | Result dataclass with status, progress, step counts, duration, and error information |
| `Migration` | Complete migration definition with ID, name, version, description, and ordered steps |
| `DataTransformer` | Abstract base class for data transformations |
| `FieldRenameTransformer` | Renames dictionary keys according to a provided mapping |
| `FieldTypeTransformer` | Converts field values to specified target types |
| `CompositeTransformer` | Chains multiple transformers to apply in sequence |
| `MigrationRunner` | Executes migrations (up or down), tracks completion state, and supports rollback |
| `DataMigrator` | High-level data migration tool combining transformers for batch and single-record processing |

## Quick Start

### Schema/Infrastructure Migration

```python
from codomyrmex.migration import Migration, MigrationRunner

# Define a migration
migration = Migration(id="v1_to_v2", name="Upgrade to V2", version="2.0")
migration.add_simple_step(
    id="add_column",
    name="Add email column",
    up_fn=lambda: True,    # Replace with actual migration logic
    down_fn=lambda: True,  # Replace with rollback logic
)

# Run the migration
runner = MigrationRunner()
result = runner.run(migration)
print(result.status)         # MigrationStatus.COMPLETED
print(result.progress)       # 1.0

# Roll back if needed
rollback_result = runner.rollback(migration)
```

### Data Migration

```python
from codomyrmex.migration import DataMigrator, FieldRenameTransformer, FieldTypeTransformer

migrator = DataMigrator()
migrator.add_transformer(FieldRenameTransformer({"old_name": "new_name"}))
migrator.add_transformer(FieldTypeTransformer({"age": int}))

old_data = [
    {"old_name": "Alice", "age": "30"},
    {"old_name": "Bob", "age": "25"},
]
new_data = migrator.migrate(old_data)
# [{"new_name": "Alice", "age": 30}, {"new_name": "Bob", "age": 25}]
```

## Related Modules

- [environment_setup](../environment_setup/) - Environment validation before running migrations
- [logging_monitoring](../logging_monitoring/) - Logging migration progress and results

## Navigation

- **Source**: [src/codomyrmex/migration/](../../../src/codomyrmex/migration/)
- **API Specification**: [src/codomyrmex/migration/API_SPECIFICATION.md](../../../src/codomyrmex/migration/API_SPECIFICATION.md)
- **Parent**: [docs/modules/](../README.md)
