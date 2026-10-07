# Workflow Configuration Schema

This document describes the JSON schema for workflow definitions, parameter substitution syntax, dependency resolution rules, and provides validation examples.

## Overview

Workflows in Codomyrmex are defined as JSON files that specify a sequence of steps, each representing an action to be executed in a Codomyrmex module. Workflows are stored in `config/workflows/production/` directory (relative to the working directory, or the `config_dir` passed to `WorkflowManager`) and loaded automatically when the WorkflowManager is initialized. The API lives in `codomyrmex.logistics.orchestration.project` (formerly `codomyrmex.project_orchestration`).

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
| --- | --- | --- | --- | --- |
| `name` | string | Yes | - | Unique identifier for this step within the workflow |
| `module` | string | Yes | - | Codomyrmex module name (e.g., "static_analysis", "data_visualization") |
| `action` | string | Yes | - | Specific action/function to call within the module |
| `parameters` | object | No | `{}` | Parameters to pass to the action function |
| `dependencies` | array | No | `[]` | List of step names that must complete before this step |
| `timeout` | integer/null | No | `null` | Maximum execution time in seconds (null = no limit) |
| `max_retries` | integer | No | `0` | Loaded into `WorkflowStep.retry_count`; automatic retries are not implemented yet |

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
      "module": "agents",
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

Workflow steps are designed to support parameter substitution using the `{{variable}}` syntax, so that steps can reference outputs from previous steps or global workflow parameters.

> **Not yet implemented**: the current `WorkflowManager` passes `{{...}}` strings through unchanged. `execute_workflow(name, **params)` merges its keyword arguments into every step's `parameters` (overriding keys with the same name).

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
workflow_manager.execute_workflow(
    "data_pipeline",
    input_file="./data/input.csv",
    processing_operations=["normalize", "filter"],
    output_directory="./output"
)
```

each step receives `input_file`, `processing_operations`, and `output_directory` as additional parameters.

## Dependency Resolution

Dependencies define the execution order of workflow steps.

### Dependency Rules

1. **Definition Order**: `execute_workflow()` submits steps in list order and maps each dependency to the task ID of an already-submitted step, so list a step after the steps it depends on.

2. **Missing or Circular Dependencies**: Dependencies that do not name an earlier step are dropped silently at execution time. Use `validate_workflow_dependencies()` (missing and self-dependencies) and `get_workflow_execution_order()` (raises `ValueError` on cycles) to check a definition first.

3. **Dependency Resolution Algorithm**:
   - Steps with no dependencies are executed first
   - Steps whose dependencies are all completed become ready
   - Steps are executed as soon as all dependencies are satisfied
   - Multiple independent steps can execute in parallel (if supported by the execution engine)

### Example Dependency Graph

```text
Step A (no dependencies)
  └─> Step B (depends on A)
       └─> Step C (depends on B)
  └─> Step D (depends on A)
       └─> Step E (depends on D)
```

Execution order: A → (B, D) → C → E

### Parallel Execution

Steps with no dependencies on each other can execute in parallel: `execute_workflow()` hands every step to the shared `TaskOrchestrator`, which runs ready tasks on its worker pool. `WorkflowManager.execute_parallel_workflow()` runs a workflow dictionary through a `ParallelExecutor` instead.

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

All step names within a workflow must be unique; dependencies are resolved by name.

### Dependency Validation

`create_workflow()` stores the steps as given. Check definitions with:

- `validate_workflow_dependencies(steps)`: reports dependencies on missing steps and self-dependencies
- `get_workflow_execution_order(steps)`: returns parallel execution levels and raises `ValueError` on cycles

### Example Validation

```python
from codomyrmex.logistics.orchestration.project import WorkflowManager, WorkflowStep

manager = WorkflowManager()

# Valid workflow
steps = [
    WorkflowStep(name="step1", module="module1", action="action1"),
    WorkflowStep(name="step2", module="module2", action="action2", dependencies=["step1"])
]
manager.create_workflow("valid_workflow", steps)  # Returns True

# The DAG helpers take step dictionaries
step_dicts = [{"name": s.name, "dependencies": s.dependencies} for s in steps]
manager.validate_workflow_dependencies(step_dicts)  # [] -> valid
manager.get_workflow_execution_order(step_dicts)  # [['step1'], ['step2']]

# Invalid: Circular dependency
circular = [
    {"name": "step1", "dependencies": ["step2"]},
    {"name": "step2", "dependencies": ["step1"]}
]
manager.get_workflow_execution_order(circular)  # Raises ValueError (cycle detected)

# Invalid: Missing required field
WorkflowStep(name="step1", module="module1")  # Raises TypeError (missing 'action')
```

## Workflow File Location

Workflows are stored in JSON files in the `config/workflows/production/` directory. The filename should match the workflow name (e.g., `ai_analysis_workflow.json`).

### Loading Workflows

Workflows are automatically loaded when WorkflowManager is initialized:

```python
from codomyrmex.logistics.orchestration.project import WorkflowManager

# Workflows are loaded from config/workflows/production/ automatically
manager = WorkflowManager()

# List all loaded workflows
workflows = manager.list_workflows()
```

### Saving Workflows

`create_workflow()` registers a workflow in memory only; there is no `save` option. To persist a workflow, write a JSON file in the format above to `manager.config_dir`.

## Error Handling and Retry Logic

### Step-Level Error Handling

Each step can specify:

- `timeout`: Recorded on the step's `Task`
- `max_retries`: Recorded as `WorkflowStep.retry_count`

### Current Behaviour

- Automatic retries are not implemented yet; a failed step's task is marked `FAILED`
- Failed steps do not prevent execution of independent steps; dependent steps stay `BLOCKED`
- `execute_workflow()` returns a `WorkflowExecution` immediately with status `RUNNING` and does not update it as steps finish (`step_results` stays empty). Check step outcomes on the task orchestrator with `get_task_orchestrator().list_tasks()` and `get_task_result(task_id)`
- If submission itself fails, the execution's `status` is `FAILED` and `error` holds the message

## Best Practices

1. **Naming**: Use descriptive, unique step names that clearly indicate the step's purpose
2. **Dependencies**: Keep dependency chains as short as possible to maximize parallelism
3. **Timeouts**: Set appropriate timeouts based on expected execution time
4. **Error Handling**: Configure `max_retries` based on step reliability
5. **Workflow Parameters**: Pass shared values as `execute_workflow()` keyword arguments rather than hardcoding them
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
