# Migration Module — Agent Coordination

## Purpose

Provider and data migration tools.

## Key Capabilities

- **MigrationStatus**: Status of a migration.
- **MigrationDirection**: Direction of migration.
- **MigrationStep**: A single migration step.
- **MigrationResult**: Result of a migration.
- **Migration**: A complete migration definition.
- `run_up()`: Run migration up.
- `run_down()`: Run migration down (rollback).
- `progress()`: Get progress percentage.

## Agent Usage Patterns

```python
from codomyrmex.migration import MigrationStatus

# Agent initializes migration
instance = MigrationStatus()
```

## Integration Points

- **Source**: [src/codomyrmex/migration/](../../../src/codomyrmex/migration/)
- **Docs**: [Module Documentation](README.md)
- **Spec**: [Technical Specification](SPEC.md)

## Testing Guidelines

```bash
uv run python -m pytest src/codomyrmex/tests/ -k migration -v
```

- Run tests before and after making changes.
- Ensure all existing tests pass before submitting.
