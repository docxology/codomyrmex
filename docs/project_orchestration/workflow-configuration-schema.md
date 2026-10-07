# Workflow Configuration Schema

This document describes the JSON format of workflow definition files, how they are loaded and saved, and how their steps are executed.

## Overview

A workflow is a set of steps, each calling one Codomyrmex function. `WorkflowManager` (in `codomyrmex.logistics.orchestration.project`) loads every `*.json` file in its `config_dir` when it is constructed. The default `config_dir` is `config/workflows/production/` under the current working directory; this is also where `codomyrmex workflow create` saves new workflows and where `codomyrmex workflow list` / `run` look for them.

## JSON Schema

### Root Object

```json
{
  "name": "string (optional, defaults to the file stem)",
  "steps": [
    {
      "name": "string (required)",
      "module": "string (required)",
      "action": "string (required)",
      "parameters": {},
      "dependencies": [],
      "timeout": null,
      "max_retries": 0,
      "required": true
    }
  ]
}
```

`steps` is required (it may be empty). Other top-level keys, such as `description`, are ignored by the loader and are not written back when a workflow is saved.

### Step Object Schema

| Field | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `name` | string | Yes | - | Unique identifier for this step within the workflow |
| `module` | string | Yes | - | Module path relative to the `codomyrmex` package (e.g. `"environment_setup"`, `"coding.static_analysis"`), or a module name registered on the task orchestrator |
| `action` | string | Yes | - | Public callable in that module, called as `action(**parameters)` |
| `parameters` | object | No | `{}` | Keyword arguments for the action, passed verbatim |
| `dependencies` | array of strings | No | `[]` | Names of steps that must complete before this step runs |
| `timeout` | number/null | No | `null` | Recorded on the task; not enforced |
| `max_retries` | integer ≥ 0 | No | `0` | Stored as `WorkflowStep.retry_count`; recorded, retries are not performed |
| `required` | boolean | No | `true` | When `false`, the workflow can still succeed if this step fails |

A step that sets `run_if` makes the file invalid: conditions are not supported. Any file that is not valid JSON or breaks the rules above is logged and skipped; the other files still load. If two files define the same workflow name, the file that sorts later wins and a warning is logged.

### Example Workflow Definition

```json
{
  "name": "complex_analysis",
  "steps": [
    {
      "name": "setup",
      "module": "environment_setup",
      "action": "validate_environment",
      "parameters": {},
      "dependencies": [],
      "timeout": 60,
      "max_retries": 0
    },
    {
      "name": "analyze_code",
      "module": "coding.static_analysis",
      "action": "analyze_project",
      "parameters": {"project_root": "."},
      "dependencies": ["setup"]
    },
    {
      "name": "scan_secrets",
      "module": "security",
      "action": "scan_secrets",
      "parameters": {"target_path": "."},
      "dependencies": ["setup"]
    },
    {
      "name": "environment_report",
      "module": "environment_setup",
      "action": "generate_environment_report",
      "dependencies": ["analyze_code", "scan_secrets"]
    }
  ]
}
```

More examples, all of which run as shipped, are in [`config/workflows/examples/`](../../config/workflows/examples/README.md).

## Parameters

Step parameters are static. There is **no** `{{variable}}` or `{{step_name.output}}` substitution: a string such as `"{{analyze_code.output}}"` reaches the action unchanged. Steps therefore cannot consume each other's results; a step's return value is available afterwards in `WorkflowExecution.step_results[step_name]["result"]`.

Parameters given when the workflow is run (`execute_workflow(name, **params)`, `codomyrmex workflow run <name> --params '{...}'`) are merged over **every** step's `parameters`, so every step must accept them.

## Dependency Resolution

Steps run in dependency order, whatever order they are listed in; independent steps run concurrently on the task orchestrator.

1. **Invalid dependencies**: a dependency on a step name that does not exist, a cycle (including a step depending on itself) or duplicate step names raise `ValueError` before any step runs.
2. **Failed dependencies**: a step whose dependency failed is failed without running; steps that do not depend on it still run.
3. **Outcome**: the execution is `COMPLETED` when every `required` step completed, otherwise `FAILED`, with `error` naming each failed step.

### Example Dependency Graph

```text
Step A (no dependencies)
  └─> Step B (depends on A)
       └─> Step C (depends on B)
  └─> Step D (depends on A)
       └─> Step E (depends on D)
```

Execution order: A → (B, D) → (C, E)

## Loading and Saving Workflows

```python
from codomyrmex.logistics.orchestration.project import WorkflowManager, WorkflowStep

# Loads config/workflows/production/*.json under the current directory
manager = WorkflowManager()
print(manager.list_workflows())
print(manager.workflow_files)  # workflow name -> definition file

steps = [
    WorkflowStep(name="setup", module="environment_setup", action="validate_environment"),
    WorkflowStep(
        name="analyze",
        module="coding.static_analysis",
        action="analyze_project",
        parameters={"project_root": "."},
        dependencies=["setup"],
    ),
]

# In memory only (default)
manager.create_workflow("my_workflow", steps)

# Also write config/workflows/production/my_workflow.json
manager.create_workflow("my_workflow", steps, persist=True)

# Write an already registered workflow (back to the file it came from, if any)
manager.save_workflow("my_workflow")
```

`save_workflow` validates the workflow before writing and writes atomically. It raises:

- `KeyError` if the workflow is not registered;
- `ValueError` if the name cannot be used as a file name (letters, digits, `.`, `_`, `-`, starting with a letter or digit), a step is malformed, the dependencies are invalid, or the target file already holds a different or unreadable workflow (it is never overwritten);
- `NotImplementedError` if a step sets `run_if`;
- `TypeError` if a parameter is not JSON-serialisable (`ValueError` for NaN or infinity).

With `create_workflow(..., persist=True)`, a failed save restores the previous registration before the error propagates.

## Validation

The shipped definitions are checked by `tests/unit/logistics/test_shipped_workflow_configs.py`: every file must load, every step must name a real `codomyrmex.<module>.<action>` (except `tests/error_test_workflow.json`, which fails on purpose and says so in its `description`), and every workflow is run.

To check a workflow of your own, load it and resolve its actions:

```python
from codomyrmex.logistics.orchestration.project.task_orchestrator import resolve_module_action

for step in manager.get_workflow("my_workflow"):
    resolve_module_action(step.module, step.action)  # raises TaskExecutionError if missing
```

## Best Practices

1. **Naming**: Use descriptive, unique step names that clearly indicate the step's purpose
2. **Dependencies**: Keep dependency chains short so independent steps run in parallel
3. **Side effects**: Prefer actions that only read the working directory for workflows that are run often
4. **Parameters**: Keep step parameters self-contained; run-time `--params` reach every step
5. **Modularity**: Design workflows to be reusable across different contexts

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
