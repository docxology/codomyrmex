# Codomyrmex Agents — src/codomyrmex/orchestrator

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose

Service Layer module providing functionality for discovering, configuring, and running workflows within the Codomyrmex project. Manages DAG-based task orchestration and script execution.

## Active Components

### Core Orchestration

- `core.py` - Main orchestrator implementation
  - Key Functions: `run_orchestrator()` (aliased as `main`)

### Configuration

- `config.py` - Configuration management
  - Key Functions: `load_config()`, `get_script_config()`

### Workflow Engine

- `workflow.py` - Workflow and task management
  - Key Classes: `Workflow`, `Task`, `TaskStatus`, `WorkflowError`

### Discovery

- `discovery.py` - Script and module discovery
  - Functions for finding executable scripts

### Reporting

- `reporting.py` - Workflow execution reporting
  - Functions for generating execution reports

### Runner

- `runner.py` - Script execution runner
  - Functions for running discovered scripts

## Key Classes and Functions

| Class/Function | Purpose |
| :--- | :--- |
| `Workflow` | DAG-based workflow definition and execution |
| `Task` | Individual task within a workflow |
| `TaskStatus` | Enum: pending, running, completed, failed, skipped |
| `WorkflowError` | Workflow execution exception |
| `run_orchestrator()` | Main entry point for orchestration |
| `load_config()` | Load workflow configuration |
| `get_script_config()` | Get configuration for specific script |

## Operating Contracts

1. **Logging**: Uses `logging_monitoring` for workflow execution logging
2. **DAG Execution**: Tasks execute in dependency order
3. **Parallel Execution**: Independent tasks can run in parallel
4. **Error Handling**: Failed tasks can be retried or skipped based on config
5. **Integration**: Works with `logistics` for task scheduling

## Signposting

### Document Hierarchy

- **Self**: [AGENTS.md](AGENTS.md)
- **Parent**: [src/codomyrmex/AGENTS.md](../AGENTS.md)
- **Project Root**: [../../../AGENTS.md](../../../AGENTS.md)

### Sibling Modules

| Module | AGENTS.md | Purpose |
| :--- | :--- | :--- |
| logistics | [../logistics/AGENTS.md](../logistics/AGENTS.md) | Task scheduling |
| events | [../events/AGENTS.md](../events/AGENTS.md) | Event system |
| build_synthesis | [../build_synthesis/AGENTS.md](../build_synthesis/AGENTS.md) | Build automation |

### Related Documentation

- [README.md](README.md) - User documentation
- [API_SPECIFICATION.md](API_SPECIFICATION.md) - API documentation
- [SPEC.md](SPEC.md) - Functional specification
- [../../docs/project_orchestration/](../../docs/project_orchestration/) - Orchestration guides
