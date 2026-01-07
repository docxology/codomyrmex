# Codomyrmex Agents — config/workflows

## Signposting
- **Parent**: [config](../AGENTS.md)
- **Self**: [workflows Agents](AGENTS.md)
- **Children**:
    - [examples](examples/AGENTS.md)
    - [tests](tests/AGENTS.md)
    - [production](production/AGENTS.md)
- **Key Artifacts**:
    - [Human Readme](README.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose

Workflow definitions directory for Codomyrmex project orchestration. Contains organized workflow JSON files separated into examples, tests, and production categories.

## Active Components

- `README.md` – Main workflow documentation
- `examples/` – Example workflow implementations
- `tests/` – Test workflows for validation
- `production/` – Active production workflows

## Workflow Structure

Workflows are JSON files containing:
- **name**: Workflow identifier
- **steps**: Array of workflow step definitions

Each step includes:
- **name**: Step identifier
- **module**: Codomyrmex module name
- **action**: Module function to execute
- **parameters**: Step parameters (supports `{{variable}}` substitution)
- **dependencies**: List of prerequisite step names
- **timeout**: Optional timeout in seconds
- **retry_count**: Current retry count (runtime)
- **max_retries**: Maximum retry attempts

## Operating Contracts

1. **Workflow Loading**: Workflows are auto-loaded from `production/` directory by default
2. **Validation**: Invalid workflows are skipped with error logging
3. **Organization**: Workflows should be placed in appropriate subdirectories (examples, tests, production)

## Integration Points

- **WorkflowManager**: Loads and executes workflows from this directory
- **OrchestrationEngine**: Coordinates workflow execution
- **Project Templates**: May reference workflows from this directory

## Navigation Links

- **Human Documentation**: [README.md](README.md)
- **Examples**: [examples/](examples/README.md)
- **Tests**: [tests/](tests/README.md)
- **Production**: [production/](production/README.md)
- **Parent**: [config](../AGENTS.md)
- **Project Root**: [README](../../../README.md)

