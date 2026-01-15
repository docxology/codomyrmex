# Workflow Configuration Schema

This document describes the JSON schema for workflow definitions, parameter substitution syntax, dependency resolution rules, and provides validation examples.

## Overview

Workflows in Codomyrmex are defined as JSON files that specify a sequence of steps, each representing an action to be executed in a Codomyrmex module. Workflows are stored in `config/workflows/production/` directory and loaded automatically when the WorkflowManager is initialized.

## JSON Schema

### Root Object

```json
{
  "name": "string (required)",
  "steps": [
    {
      "name": "string (required)",
      "module": "string (required)",
      "action": "string (required)",
      "parameters": {},
      "dependencies": [],
      "timeout": null,
      "max_retries": 3
    }
  ]
}
```

### Step Object Schema

Each workflow step is defined with the following structure:

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `name` | string | Yes | - | Unique identifier for this step within the workflow |
| `module` | string | Yes | - | Codomyrmex module name (e.g., "static_analysis", "data_visualization") |
| `action` | string | Yes | - | Specific action/function to call within the module |
| `parameters` | object | No | `{}` | Parameters to pass to the action function |
| `dependencies` | array | No | `[]` | List of step names that must complete before this step |
| `timeout` | integer/null | No | `null` | Maximum execution time in seconds (null = no limit) |
| `retry_count` | integer | No | `0` | Current retry count (internal use, typically 0) |
| `max_retries` | integer | No | `3` | Maximum number of retry attempts before marking as failed |

### Example Workflow Definition

```json
{
  "name": "ai_analysis_workflow",
  "steps": [
    {
      "name": "environment_check",
      "module": "environment_setup",
      "action": "check_environment",
      "parameters": {},
      "dependencies": [],
      "timeout": 60,
      "max_retries": 3
    },
    {
      "name": "code_analysis",
      "module": "static_analysis",
      "action": "analyze_code_quality",
      "parameters": {
        "path": ".",
        "output_format": "json"
      },
      "dependencies": ["environment_check"],
      "timeout": 300,
      "max_retries": 2
    },
    {
      "name": "ai_insights",
      "module": "ai_code_editing",
      "action": "generate_code_insights",
      "parameters": {
        "analysis_data": "{{code_analysis.output}}",
        "provider": "openai"
      },
      "dependencies": ["code_analysis"],
      "timeout": 120,
      "max_retries": 3
    },
    {
      "name": "create_report",
      "module": "data_visualization",
      "action": "create_analysis_chart",
      "parameters": {
        "data": "{{ai_insights.output}}",
        "output_path": "./reports/analysis.png"
      },
      "dependencies": ["ai_insights"],
      "timeout": 60,
      "max_retries": 1
    }
  ]
}
```

## Parameter Substitution

Workflow steps support parameter substitution using the `{{variable}}` syntax. This allows steps to reference outputs from previous steps or global workflow parameters.

### Syntax

- `{{step_name.output}}` - References the output from a previous step named `step_name`
- `{{parameter_name}}` - References a global workflow parameter
- `{{step_name.metadata.field}}` - References a specific field in step metadata

### Substitution Rules

1. **Step Outputs**: When a step completes, its output is stored in `execution.results[step_name]`. The `{{step_name.output}}` syntax accesses this value.

2. **Global Parameters**: Parameters passed to `execute_workflow()` are available via `{{parameter_name}}` syntax.

3. **Nested Access**: For complex objects, use dot notation: `{{step_name.metadata.field}}`.

4. **String Interpolation**: Substitution happens in string values. To use literal `{{`, escape it or use quotes appropriately.

### Example with Parameter Substitution

```json
{
  "name": "data_pipeline",
  "steps": [
    {
      "name": "load_data",
      "module": "data_visualization",
      "action": "load_dataset",
      "parameters": {
        "file_path": "{{input_file}}"
      }
    },
    {
      "name": "process_data",
      "module": "data_visualization",
      "action": "process_dataset",
      "parameters": {
        "data": "{{load_data.output}}",
        "operations": "{{processing_operations}}"
      },
      "dependencies": ["load_data"]
    },
    {
      "name": "visualize",
      "module": "data_visualization",
      "action": "create_chart",
      "parameters": {
        "data": "{{process_data.output}}",
        "output_path": "{{output_directory}}/visualization.png"
      },
      "dependencies": ["process_data"]
    }
  ]
}
```

When executed with:
```python
await workflow_manager.execute_workflow(
    "data_pipeline",
    parameters={
        "input_file": "./data/input.csv",
        "processing_operations": ["normalize", "filter"],
        "output_directory": "./output"
    }
)
```

The parameters are substituted accordingly.

## Dependency Resolution

Dependencies define the execution order of workflow steps. Steps are executed in dependency order, not definition order.

### Dependency Rules

1. **Circular Dependencies**: Circular dependencies are detected and will cause workflow execution to fail with a `ValueError`.

2. **Missing Dependencies**: If a step depends on a step name that doesn't exist, a warning is logged but execution continues. The step will never become ready and will eventually timeout.

3. **Dependency Resolution Algorithm**:
   - Steps with no dependencies are executed first
   - Steps whose dependencies are all completed become ready
   - Steps are executed as soon as all dependencies are satisfied
   - Multiple independent steps can execute in parallel (if supported by the execution engine)

### Example Dependency Graph

```
Step A (no dependencies)
  └─> Step B (depends on A)
       └─> Step C (depends on B)
  └─> Step D (depends on A)
       └─> Step E (depends on D)
```

Execution order: A → (B, D) → C → E

### Parallel Execution

Steps with no dependencies on each other can execute in parallel. The WorkflowManager executes steps sequentially by default, but the OrchestrationEngine can execute independent steps in parallel when configured with `mode="parallel"` or `mode="resource_aware"`.

## Validation

### Required Fields Validation

A workflow definition must have:
- `name`: Non-empty string
- `steps`: Non-empty array with at least one step

Each step must have:
- `name`: Non-empty string
- `module`: Non-empty string
- `action`: Non-empty string

### Step Name Uniqueness

All step names within a workflow must be unique. Duplicate step names will cause workflow creation to fail.

### Dependency Validation

- Dependencies must reference existing step names
- Circular dependencies are detected and cause failure
- Self-referential dependencies (step depends on itself) are treated as circular

### Example Validation

```python
from codomyrmex.project_orchestration import WorkflowManager, WorkflowStep

manager = WorkflowManager()

# Valid workflow
steps = [
    WorkflowStep(name="step1", module="module1", action="action1"),
    WorkflowStep(name="step2", module="module2", action="action2", dependencies=["step1"])
]
manager.create_workflow("valid_workflow", steps)  # Success

# Invalid: Circular dependency
steps = [
    WorkflowStep(name="step1", module="module1", action="action1", dependencies=["step2"]),
    WorkflowStep(name="step2", module="module2", action="action2", dependencies=["step1"])
]
manager.create_workflow("circular_workflow", steps)  # Will fail during execution

# Invalid: Missing required field
steps = [
    WorkflowStep(name="step1", module="module1")  # Missing 'action'
]
manager.create_workflow("invalid_workflow", steps)  # Will fail
```

## Workflow File Location

Workflows are stored in JSON files in the `config/workflows/production/` directory. The filename should match the workflow name (e.g., `ai_analysis_workflow.json`).

### Loading Workflows

Workflows are automatically loaded when WorkflowManager is initialized:

```python
from codomyrmex.project_orchestration import WorkflowManager

# Workflows are loaded from config/workflows/production/ automatically
manager = WorkflowManager()

# List all loaded workflows
workflows = manager.list_workflows()
```

### Saving Workflows

Workflows are automatically saved when created with `save=True` (default):

```python
manager.create_workflow("my_workflow", steps, save=True)  # Saved to config/workflows/production/my_workflow.json
```

## Error Handling and Retry Logic

### Step-Level Error Handling

Each step can specify:
- `timeout`: Maximum execution time before the step is considered failed
- `max_retries`: Number of times to retry the step if it fails

### Retry Behavior

- Failed steps are retried up to `max_retries` times
- Retries happen automatically with exponential backoff (future enhancement)
- After all retries are exhausted, the step is marked as failed
- Failed steps do not prevent execution of independent steps

### Workflow-Level Error Handling

- If a step fails after all retries, the workflow continues executing other steps
- The workflow status is set to `FAILED` if any step fails
- All step errors are collected in `execution.errors`
- Partial results are available in `execution.results` for completed steps

## Best Practices

1. **Naming**: Use descriptive, unique step names that clearly indicate the step's purpose
2. **Dependencies**: Keep dependency chains as short as possible to maximize parallelism
3. **Timeouts**: Set appropriate timeouts based on expected execution time
4. **Error Handling**: Configure `max_retries` based on step reliability
5. **Parameter Substitution**: Use parameter substitution to avoid hardcoding values
6. **Modularity**: Design workflows to be reusable across different contexts

## Related Documentation

- [API Specification](../../src/codomyrmex/logistics/orchestration/project/API_SPECIFICATION.md)
- [Task Orchestration Guide](./task-orchestration-guide.md)
- [Dispatch and Coordination](./dispatch-coordination.md)
- [Config-Driven Operations](./config-driven-operations.md)


## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../../docs/README.md)
- **Home**: [Repository Root](../../README.md)
