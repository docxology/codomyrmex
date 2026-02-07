# Orchestrator Module — Agent Coordination

## Purpose

This module provides functionality for discovering, configuring, and running

## Key Capabilities

- Orchestrator operations and management

## Agent Usage Patterns

```python
from codomyrmex.orchestrator import *

# Agent uses orchestrator capabilities
```

## Integration Points

- **Source**: [src/codomyrmex/orchestrator/](../../../src/codomyrmex/orchestrator/)
- **Docs**: [Module Documentation](README.md)
- **Spec**: [Technical Specification](SPEC.md)


## Key Components

- **`StepError`** — Raised when a workflow step fails.
- **`OrchestratorTimeoutError`** — Raised when orchestration operations timeout.
- **`StateError`** — Raised when workflow state operations fail.
- **`DependencyResolutionError`** — Raised when task dependencies cannot be resolved.
- **`ConcurrencyError`** — Raised when concurrency-related issues occur.
- **`load_config()`** — Load script configuration, searching upwards for config.yaml.
- **`get_script_config()`** — Get configuration for a specific script.
- **`main()`** — Main entry point.
- **`discover_scripts()`** — Discover all Python scripts in the scripts directory.

### Submodules

- `engines` — Engines
- `monitors` — Monitors
- `pipelines` — Pipelines
- `schedulers` — Schedulers
- `state` — State
- `templates` — Templates
- `triggers` — Triggers
- `workflows` — Workflows

## Testing Guidelines

```bash
uv run python -m pytest src/codomyrmex/tests/ -k orchestrator -v
```

- Run tests before and after making changes.
- Ensure all existing tests pass before submitting.
