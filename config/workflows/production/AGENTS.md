# Codomyrmex Agents — config/workflows/production

## Signposting
- **Parent**: [workflows](../AGENTS.md)
- **Self**: [production Agents](AGENTS.md)
- **Children**: None
- **Key Artifacts**:
    - [Human Readme](README.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose

Active production workflows directory. Workflows in this directory are automatically loaded by `WorkflowManager` and available for execution.

## Active Components

- Production workflow JSON files (user-created)
- Automatically loaded on `WorkflowManager` initialization

## Operating Contracts

1. **Auto-Loading**: All `.json` files in this directory are automatically loaded
2. **Validation**: Invalid workflows are skipped with error logging
3. **Naming**: Workflow names must be unique
4. **Schema**: Workflows must follow the workflow schema (name, steps)

## Integration Points

- **WorkflowManager**: Primary loader and executor
- **OrchestrationEngine**: Coordinates workflow execution
- **Project Templates**: May reference workflows from this directory

## Navigation Links

- **Human Documentation**: [README.md](README.md)
- **Parent**: [workflows](../AGENTS.md)
- **Project Root**: [README](../../../../README.md)

