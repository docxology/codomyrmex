# Project Lifecycle Guide

Complete guide for managing projects from creation through execution, status tracking, and completion.

## Overview

Projects in Codomyrmex represent organized work units with defined structure and status. The API lives in `codomyrmex.logistics.orchestration.project` (formerly `codomyrmex.project_orchestration`). `ProjectManager` currently provides `create_project`, `get_project`, `list_projects`, and `update_project_status`; projects are tracked in memory for the lifetime of the manager.

> **Not yet implemented**: template-driven creation (`template_name`), archiving, and deletion. The JSON files described in the [Project Template Schema](./project-template-schema.md) are reference definitions only. Project-bound workflows run through `OrchestrationEngine.execute_project_workflow()`, which records each run in `Project.metrics`, and `create_project_from_workflow()`, which creates the project, runs the workflow and records a milestone on success; `ProjectManager` also provides `update_project_metrics()`, `add_project_milestone()` and `get_projects_summary()`.

## Step 1: Choose a Project Type

```python
from codomyrmex.logistics.orchestration.project import ProjectType, get_project_manager

pm = get_project_manager()

print([t.value for t in ProjectType])
# ['ai_analysis', 'web_application', 'data_pipeline', 'ml_model', 'documentation', 'research', 'custom']
```

## Step 2: Create the Project

```python
# Create a project under pm.projects_root (the current directory by default)
project = pm.create_project(
    name="my_ai_project",
    type=ProjectType.AI_ANALYSIS,
    description="AI analysis of my codebase"
)

if project:  # None if the directory already exists or creation failed
    print(f"Created project: {project.name}")
    print(f"Path: {project.path}")
    print(f"Type: {project.type.value}")
    print(f"Status: {project.status.value}")  # "active"
```

### Custom Project Location

```python
from pathlib import Path

from codomyrmex.logistics.orchestration.project import ProjectManager

custom_pm = ProjectManager(projects_root=Path("/path/to/custom/location"))
custom_project = custom_pm.create_project("custom_project", ProjectType.CUSTOM, "Custom location project")
```

## Step 3: Execute Work for the Project

Projects are not bound to workflows yet; run workflows or tasks directly and pass the project path as a parameter:

```python
from codomyrmex.logistics.orchestration.project import get_workflow_manager

manager = get_workflow_manager()
# Assumes an "ai-analysis" workflow is registered (JSON config or create_workflow)
execution = manager.execute_workflow("ai-analysis", code_path=str(project.path / "src"))
print(execution.execution_id, execution.status.value)
```

See the [Task Orchestration Guide](./task-orchestration-guide.md) and [Workflow Configuration Schema](./workflow-configuration-schema.md).

## Step 4: Track Status

```python
from codomyrmex.logistics.orchestration.project import ProjectStatus

pm.update_project_status("my_ai_project", ProjectStatus.PAUSED)

project = pm.get_project("my_ai_project")
print(project.to_dict())
# {'name': ..., 'path': ..., 'type': 'ai_analysis', 'status': 'paused', 'config': {}, 'created_at': ..., ...}
```

`ProjectStatus` values: `planning`, `active`, `paused`, `completed`, `archived`, `failed`.

## Step 5: Complete or Archive the Project

```python
pm.update_project_status("my_ai_project", ProjectStatus.COMPLETED)

# Archiving is a status change; files on disk are left in place
pm.update_project_status("my_ai_project", ProjectStatus.ARCHIVED)
```

## Project Management

### List Projects

```python
for project in pm.list_projects():
    print(f"{project.name}: {project.status.value} ({project.type.value})")
```

### Project File Structure

`create_project` creates the following structure and generates the README/AGENTS documentation:

```text
my_ai_project/
├── README.md              # Auto-generated project documentation
├── AGENTS.md              # Auto-generated agent configuration
├── src/                   # Source code directory
│   ├── README.md          # Nested documentation
│   └── AGENTS.md          # Nested agent config
├── tests/
│   ├── README.md
│   └── AGENTS.md
├── config/
│   ├── README.md
│   └── AGENTS.md
└── docs/
    ├── README.md
    └── AGENTS.md
```

## Complete Example

```python
from codomyrmex.logistics.orchestration.project import (
    ProjectStatus,
    ProjectType,
    get_project_manager,
)

# Initialize project manager
pm = get_project_manager()

# 1. Create project
project = pm.create_project(
    name="codebase_analysis",
    type=ProjectType.AI_ANALYSIS,
    description="Comprehensive analysis of codebase quality"
)
print(f"Created project: {project.name} at {project.path}")

# 2. Do the work (tasks or workflows), then record progress
pm.update_project_status("codebase_analysis", ProjectStatus.PAUSED)

# 3. Complete project
pm.update_project_status("codebase_analysis", ProjectStatus.COMPLETED)
print(pm.get_project("codebase_analysis").status.value)  # "completed"
```

## Best Practices

1. **Project Type**: Choose the `ProjectType` that matches your project
2. **Naming**: Use descriptive project names (the name is also the directory name)
3. **Status**: Keep `ProjectStatus` current so dashboards and agents see the right state
4. **Documentation**: Review the auto-generated README/AGENTS files
5. **Workflows**: Execute workflows appropriate for the project stage

## Related Documentation

- [Project Template Schema](./project-template-schema.md)
- [Config-Driven Operations](./config-driven-operations.md)
- [API Specification](../../src/codomyrmex/logistics/orchestration/project/API_SPECIFICATION.md)

## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../../docs/README.md)
- **Home**: [Repository Root](../../README.md)
