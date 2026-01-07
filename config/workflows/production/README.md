# production

## Signposting
- **Parent**: [workflows](../README.md)
- **Children**: None
- **Key Artifacts**:
    - [Agent Guide](AGENTS.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Overview

Active production workflows. Workflows in this directory are automatically loaded by `WorkflowManager` and available for execution.

## Creating Production Workflows

1. Create a JSON file in this directory
2. Follow the workflow schema (see parent README)
3. Workflow will be automatically loaded on next `WorkflowManager` initialization

### Workflow Naming

Use descriptive, kebab-case names:
- ✅ `code-analysis-pipeline.json`
- ✅ `deployment-workflow.json`
- ❌ `workflow1.json`
- ❌ `test.json`

## Workflow Schema

```json
{
  "name": "workflow_name",
  "steps": [
    {
      "name": "step_name",
      "module": "module_name",
      "action": "action_name",
      "parameters": {},
      "dependencies": [],
      "timeout": 60,
      "max_retries": 3
    }
  ]
}
```

## Best Practices

1. **Version Control**: Keep workflows in version control
2. **Documentation**: Add comments in workflow files explaining complex steps
3. **Testing**: Test workflows in development before adding to production
4. **Naming**: Use clear, descriptive names
5. **Parameters**: Use parameter substitution for flexibility: `{{variable}}`
6. **Dependencies**: Explicitly define step dependencies
7. **Timeouts**: Set appropriate timeouts for long-running steps
8. **Retries**: Configure retry counts based on step reliability

## Example: Creating a New Workflow

```json
{
  "name": "my_production_workflow",
  "steps": [
    {
      "name": "validate",
      "module": "environment_setup",
      "action": "check_environment",
      "parameters": {},
      "dependencies": [],
      "timeout": 60,
      "max_retries": 3
    },
    {
      "name": "process",
      "module": "static_analysis",
      "action": "analyze_code_quality",
      "parameters": {
        "path": "{{project_path}}"
      },
      "dependencies": ["validate"],
      "timeout": 300,
      "max_retries": 2
    }
  ]
}
```

## Loading Workflows

Workflows are automatically loaded when `WorkflowManager` initializes:

```python
from codomyrmex.project_orchestration import get_workflow_manager

# Workflows from this directory are automatically loaded
manager = get_workflow_manager()
workflows = manager.list_workflows()
```

## Navigation

- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Parent Directory**: [workflows](../README.md)
- **Examples**: [examples/](../examples/README.md)
- **Project Root**: [README](../../../README.md)

