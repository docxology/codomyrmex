# Migration — Functional Specification

**Module**: `codomyrmex.migration`  
**Version**: v0.1.0  
**Status**: Active

## 1. Overview

Provider and data migration tools.

## 2. Architecture

### Components

| Component | Type | Description |
|-----------|------|-------------|
| `MigrationStatus` | Class | Status of a migration. |
| `MigrationDirection` | Class | Direction of migration. |
| `MigrationStep` | Class | A single migration step. |
| `MigrationResult` | Class | Result of a migration. |
| `Migration` | Class | A complete migration definition. |
| `DataTransformer` | Class | Base class for data transformation. |
| `FieldRenameTransformer` | Class | Renames fields in dictionaries. |
| `FieldTypeTransformer` | Class | Converts field types. |
| `CompositeTransformer` | Class | Combines multiple transformers. |
| `MigrationRunner` | Class | Runs migrations. |
| `run_up()` | Function | Run migration up. |
| `run_down()` | Function | Run migration down (rollback). |
| `progress()` | Function | Get progress percentage. |
| `duration_seconds()` | Function | Get duration in seconds. |
| `to_dict()` | Function | Convert to dictionary. |

## 3. Dependencies

See `src/codomyrmex/migration/__init__.py` for import dependencies.

## 4. Public API

```python
from codomyrmex.migration import MigrationStatus, MigrationDirection, MigrationStep, MigrationResult, Migration
```

## 5. Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k migration -v
```
