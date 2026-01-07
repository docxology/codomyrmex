# workflows

## Signposting
- **Parent**: [config](../README.md)
- **Children**:
    - [examples](examples/README.md)
    - [tests](tests/README.md)
    - [production](production/README.md)
- **Key Artifacts**:
    - [Agent Guide](AGENTS.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Overview

Workflow definitions for Codomyrmex project orchestration. Workflows define sequences of module actions that can be executed to automate complex multi-step processes.

## Directory Structure

```
workflows/
├── examples/      # Example workflows for reference and learning
├── tests/        # Test workflows for validation and testing
└── production/   # Active production workflows
```

## Workflow Configuration

Workflows are JSON files that define a sequence of steps. Each step specifies:
- **name**: Unique identifier for the step
- **module**: Codomyrmex module to use
- **action**: Function to call within the module
- **parameters**: Input parameters for the action
- **dependencies**: List of step names that must complete first
- **timeout**: Maximum execution time (optional)
- **max_retries**: Number of retry attempts (default: 3)

### Example Workflow

```json
{
  "name": "my_workflow",
  "steps": [
    {
      "name": "setup",
      "module": "environment_setup",
      "action": "check_environment",
      "parameters": {},
      "dependencies": [],
      "timeout": 60,
      "max_retries": 3
    },
    {
      "name": "analyze",
      "module": "static_analysis",
      "action": "analyze_code_quality",
      "parameters": {
        "path": "."
      },
      "dependencies": ["setup"],
      "timeout": 300,
      "max_retries": 2
    }
  ]
}
```

## Loading Workflows

Workflows are automatically loaded from `config/workflows/production/` when `WorkflowManager` initializes.

### Using Workflows

```python
from codomyrmex.project_orchestration import get_workflow_manager

# Workflows are loaded automatically
manager = get_workflow_manager()

# List available workflows
workflows = manager.list_workflows()

# Execute a workflow
import asyncio
execution = await manager.execute_workflow("my_workflow")
```

## Directory Organization

- **examples/**: Reference implementations demonstrating workflow patterns
- **tests/**: Workflows used for system validation and testing
- **production/**: Active workflows used in production environments

## Related Documentation

- [Config-Driven Operations Guide](../../docs/project_orchestration/config-driven-operations.md)
- [Workflow Manager API](../../src/codomyrmex/project_orchestration/API_SPECIFICATION.md)
- [Project Orchestration Documentation](../../docs/project_orchestration/)

## Navigation

- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Examples**: [examples/README.md](examples/README.md)
- **Tests**: [tests/README.md](tests/README.md)
- **Production**: [production/README.md](production/README.md)
- **Parent Directory**: [config](../README.md)
- **Project Root**: [README](../../README.md)

