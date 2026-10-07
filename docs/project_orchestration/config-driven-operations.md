# Config-Driven Operations Guide

Comprehensive guide for configuration-driven operations covering workflows, projects, and resources across the Codomyrmex orchestration system.

## Overview

Codomyrmex supports configuration-driven operations: workflow definitions in JSON files are loaded automatically and can be executed by name. Project templates and resource definitions are also kept as JSON, but are not loaded automatically yet. The API lives in `codomyrmex.logistics.orchestration.project` (formerly `codomyrmex.project_orchestration`).

## Configuration File Locations

### Workflow Configurations

- **Location**: `config/workflows/production/*.json`
- **Auto-loaded**: Yes, when WorkflowManager initializes
- **Format**: JSON workflow definitions

### Project Templates

- **Location**: `src/codomyrmex/logistics/orchestration/project/templates/*.json`
- **Auto-loaded**: No; reference definitions (see [Project Template Schema](./project-template-schema.md))
- **Format**: JSON template definitions

### Resource Configuration

- **Location**: none by default; `ResourceManager` starts with built-in resources
- **Auto-loaded**: No; load your own definitions with `Resource.from_dict()` (see [Resource Configuration](./resource-configuration.md))
- **Format**: JSON resource definitions matching `Resource.to_dict()`

## Workflow Configuration

### Creating Workflow Configurations

Create a JSON file in `config/workflows/production/` (relative to the working directory):

```json
{
  "name": "my_custom_workflow",
  "steps": [
    {
      "name": "step1",
      "module": "coding.static_analysis",
      "action": "analyze_code_quality",
      "parameters": {
        "path": "."
      },
      "dependencies": [],
      "timeout": 300,
      "max_retries": 3
    },
    {
      "name": "step2",
      "module": "data_visualization",
      "action": "create_bar_chart",
      "parameters": {
        "data": "{{step1.output}}",
        "title": "Analysis Results"
      },
      "dependencies": ["step1"],
      "timeout": 60,
      "max_retries": 1
    }
  ]
}
```

Each step calls `codomyrmex.<module>.<action>(**parameters)` (here `codomyrmex.coding.static_analysis.analyze_code_quality(path=".")`), unless an implementation is registered with `TaskOrchestrator.register_action`. `{{step1.output}}` placeholders are passed through unchanged for now, and `step2` above fails because `create_bar_chart` takes `categories` and `values`, not `data`; see [Parameter Substitution](./workflow-configuration-schema.md#parameter-substitution).

### Loading Workflows

Workflows are automatically loaded:

```python
from codomyrmex.logistics.orchestration.project import get_workflow_manager

# Workflows are loaded automatically
manager = get_workflow_manager()

# List loaded workflows (names)
workflows = manager.list_workflows()
print(f"Loaded workflows: {workflows}")
```

### Executing Configured Workflows

`execute_workflow` runs the steps in dependency order on the shared task orchestrator and returns once every step has finished. The returned execution is `completed` when every required step completed and `failed` otherwise; a step whose dependency failed is not run. Missing dependencies or cycles raise `ValueError` before any step runs.

```python
from codomyrmex.logistics.orchestration.project import get_workflow_manager

manager = get_workflow_manager()

# Execute workflow from configuration; keyword arguments are merged into every step's parameters
execution = manager.execute_workflow("my_custom_workflow", custom_param="value")
print(f"{execution.workflow_name}: {execution.status.value} ({execution.execution_id})")

for step_name, step in execution.step_results.items():
    print(f"{step_name}: {step['status']} {step['error'] or ''}")
if execution.error:
    print(f"Failed steps: {execution.error}")
```

## Project Template Configuration

### Creating Project Templates

Template definitions live in `src/codomyrmex/logistics/orchestration/project/templates/`:

```json
{
  "name": "my_custom_template",
  "type": "custom",
  "description": "My custom project template",
  "version": "1.0",
  "directory_structure": [
    "src/",
    "tests/",
    "docs/",
    ".codomyrmex/"
  ],
  "workflows": [
    "custom-workflow"
  ],
  "required_modules": [
    "static_analysis"
  ],
  "optional_modules": [
    "data_visualization"
  ],
  "default_config": {
    "project": {
      "name": "{{project_name}}",
      "type": "{{project_type}}"
    },
    "analysis": {
      "include_patterns": ["*.py"]
    }
  },
  "documentation_config": {
    "nested_docs": ["src/", "tests/", "docs/"],
    "doc_links": {
      "enabled": true,
      "parent_link": true,
      "child_links": true
    }
  }
}
```

### Using Templates

`ProjectManager` does not read template files yet; projects are created from a `ProjectType`:

```python
from codomyrmex.logistics.orchestration.project import ProjectType, get_project_manager

pm = get_project_manager()

project = pm.create_project(
    name="my_project",
    type=ProjectType.CUSTOM,
    description="Project for my custom workflow"
)
```

## Resource Configuration

### Creating Resource Configurations

The JSON below shows an earlier `resources.json` layout that the current `ResourceManager` does not read; see [Resource Configuration](./resource-configuration.md#resource-object) for the format accepted by `Resource.from_dict()`:

```json
{
  "resources": {
    "custom_cpu": {
      "id": "custom_cpu",
      "name": "Custom CPU Resource",
      "type": "cpu",
      "description": "Dedicated CPU for heavy workloads",
      "status": "available",
      "capacity": {
        "cores": 16
      },
      "allocated": {},
      "limits": {
        "max_cpu_cores": 16,
        "max_concurrent_users": 4
      },
      "total_allocations": 0,
      "total_usage_time": 0.0,
      "current_users": [],
      "metadata": {},
      "tags": [],
      "created_at": "2025-01-15T10:00:00+00:00",
      "updated_at": "2025-01-15T10:00:00+00:00"
    },
    "custom_api": {
      "id": "custom_api",
      "name": "Custom API",
      "type": "external_api",
      "description": "Custom external API quota",
      "status": "available",
      "capacity": {
        "requests_per_minute": 200,
        "tokens_per_minute": 50000
      },
      "allocated": {},
      "limits": {
        "max_requests_per_minute": 200,
        "timeout_seconds": 60
      },
      "total_allocations": 0,
      "total_usage_time": 0.0,
      "current_users": [],
      "metadata": {},
      "tags": [],
      "created_at": "2025-01-15T10:00:00+00:00",
      "updated_at": "2025-01-15T10:00:00+00:00"
    }
  },
  "updated_at": "2025-01-15T10:00:00+00:00"
}
```

### Loading Resources

```python
import json

from codomyrmex.logistics.orchestration.project import Resource, get_resource_manager

rm = get_resource_manager()  # starts with sys-compute, sys-memory, api-global

# Load your own definitions (a list of Resource.to_dict()-style objects)
with open("resources.json") as f:
    for data in json.load(f)["resources"]:
        rm.add_resource(Resource.from_dict(data))

# List resources
resources = rm.list_resources()
print(f"Available resources: {[r.name for r in resources]}")
```

## Environment-Specific Configuration

### Configuration File Loading Order

ConfigurationManager loads configurations in this order (later sources override earlier):

1. Default configuration files
2. Environment-specific files (`environments/{env}/*.json`)
3. Environment variables
4. Runtime overrides

### Environment Variables

The orchestration classes do not read these variables themselves; read them in your own code and pass them in the engine configuration (see [Environment-Based Configuration](#environment-based-configuration)).

```bash
# Workflow configuration
export CODOMYRMEX_WORKFLOWS_DIR="./custom/workflows"

# Project configuration
export CODOMYRMEX_PROJECTS_DIR="./custom/projects"

# Resource configuration
export CODOMYRMEX_RESOURCE_CONFIG="./custom/resources.json"

# Orchestration configuration
export CODOMYRMEX_MAX_WORKERS=8
export CODOMYRMEX_ORCHESTRATION_DIR="./.codomyrmex"
```

### Multi-Source Configuration

```python
from codomyrmex.config_management import ConfigurationManager

cm = ConfigurationManager()

# Load configuration from multiple sources
config = cm.load_configuration(
    name="orchestration",
    sources=[
        "orchestration.json",
        "environments/production/orchestration.json",
        "secrets/orchestration.json"
    ]
)
```

## Orchestration Engine Configuration

### Configuration Dictionary

```python
from pathlib import Path

from codomyrmex.logistics.orchestration.project import OrchestrationEngine

# The engine reads these keys; other keys are kept in engine.config but ignored
config = {
    "max_workers": 8,                    # TaskOrchestrator worker threads
    "workflows_dir": Path("./workflows"),  # WorkflowManager config_dir
    "projects_dir": Path("./projects"),    # ProjectManager projects_root
}

engine = OrchestrationEngine(config=config)
```

### Environment-Based Configuration

```python
import os
from pathlib import Path

# Load configuration from environment
config = {
    "max_workers": int(os.getenv("CODOMYRMEX_MAX_WORKERS", "4")),
    "workflows_dir": Path(os.getenv("CODOMYRMEX_WORKFLOWS_DIR", "config/workflows/production")),
    "projects_dir": Path(os.getenv("CODOMYRMEX_PROJECTS_DIR", "projects")),
}

engine = OrchestrationEngine(config=config)
```

## Configuration Validation

### Workflow Validation

```python
from codomyrmex.logistics.orchestration.project import WorkflowManager, WorkflowStep

manager = WorkflowManager()

steps = [
    WorkflowStep(name="step1", module="module1", action="action1"),
    WorkflowStep(name="step2", module="module2", action="action2", dependencies=["step1"])
]

# create_workflow stores the steps as given; validate dependencies explicitly
step_dicts = [{"name": s.name, "dependencies": s.dependencies} for s in steps]
errors = manager.validate_workflow_dependencies(step_dicts)  # [] when valid
order = manager.get_workflow_execution_order(step_dicts)  # raises ValueError on cycles

if not errors:
    manager.create_workflow("valid_workflow", steps)
```

### Workflow File Validation

Workflow JSON files that fail to load are skipped with a warning in the log; the remaining files are still loaded.

### Resource Validation

`Resource.from_dict()` raises `ValueError` for an unknown `type` or `status`, so validate resource files by loading them before deployment.

## Complete Config-Driven Example

### 1. Create Workflow Configuration

`config/workflows/production/data_analysis.json`:

```json
{
  "name": "data_analysis",
  "steps": [
    {
      "name": "load_data",
      "module": "data_visualization",
      "action": "load_dataset",
      "parameters": {"file_path": "{{input_file}}"},
      "dependencies": []
    },
    {
      "name": "analyze_data",
      "module": "data_visualization",
      "action": "analyze_dataset",
      "parameters": {"data": "{{load_data.output}}"},
      "dependencies": ["load_data"]
    },
    {
      "name": "visualize",
      "module": "data_visualization",
      "action": "create_chart",
      "parameters": {"data": "{{analyze_data.output}}", "output": "{{output_path}}"},
      "dependencies": ["analyze_data"]
    }
  ]
}
```

The `data_visualization` actions named here (`load_dataset`, `analyze_dataset`, `create_chart`) are placeholders: register implementations with `TaskOrchestrator.register_action("data_visualization", ...)` or replace them with existing functions, otherwise the first step fails and the workflow reports `failed`.

### 2. Create Project Template (reference only)

`src/codomyrmex/logistics/orchestration/project/templates/data_project.json`:

```json
{
  "name": "data_project",
  "type": "data_pipeline",
  "description": "Data analysis project",
  "directory_structure": ["data/", "output/", ".codomyrmex/"],
  "workflows": ["data_analysis"],
  "required_modules": ["data_visualization"]
}
```

### 3. Execute Config-Driven Workflow

```python
from codomyrmex.logistics.orchestration.project import (
    ProjectType,
    get_project_manager,
    get_workflow_manager,
)

# Create project
pm = get_project_manager()
project = pm.create_project(
    name="analysis_project",
    type=ProjectType.DATA_PIPELINE
)

# Execute workflow (automatically loaded from config); blocks until every step finished
manager = get_workflow_manager()
execution = manager.execute_workflow(
    "data_analysis",
    input_file="./data/input.csv",
    output_path="./output/result.png"
)

if execution.success:
    print(f"Analysis completed ({execution.execution_id})")
else:
    print(f"Analysis failed: {execution.error}")
```

## Best Practices

1. **Version Control**: Keep configuration files in version control
2. **Validation**: Validate configurations before deployment
3. **Documentation**: Document configuration options and examples
4. **Environment Separation**: Use environment-specific configs for different deployments
5. **Workflow Parameters**: Pass shared values as `execute_workflow()` keyword arguments
6. **Resource Management**: Configure resources based on actual system capacity
7. **Error Handling**: Check the log for workflow files that were skipped during loading

## Related Documentation

- [Workflow Configuration Schema](./workflow-configuration-schema.md)
- [Project Template Schema](./project-template-schema.md)
- [Resource Configuration](./resource-configuration.md)
- [API Specification](../../src/codomyrmex/logistics/orchestration/project/API_SPECIFICATION.md)

## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../../docs/README.md)
- **Home**: [Repository Root](../../README.md)

<!-- markdownlint-configure-file { "MD024": { "siblings_only": true } } -->
