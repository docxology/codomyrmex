# Project Lifecycle Guide

Guide for managing projects from creation through workflow execution, tracking and completion.

## Overview

A project is a scaffolded directory plus a `Project` record (name, type, status, metrics, milestones) managed by `ProjectManager` in `codomyrmex.logistics.orchestration.project`. Every project is saved as `<project directory>/project.json`, so a `ProjectManager` created later (for example by another `codomyrmex` process) finds it again.

## Step 1: Choose a Project Type

`ProjectType` values (also accepted by `codomyrmex project create --template`, where hyphens may replace underscores):

- `ai_analysis` - AI-powered code analysis
- `web_application` - Web applications
- `data_pipeline` - Data processing pipelines
- `ml_model` - Machine learning projects
- `documentation` - Documentation projects
- `research` - Research projects
- `custom` - Anything else

The type is recorded on the project and in its generated documentation; every type is scaffolded the same way.

## Step 2: Create the Project

### From the Command Line

```bash
codomyrmex project create my_ai_project --template ai_analysis --description "AI analysis of my codebase"
codomyrmex project list
```

`project create` scaffolds `./my_ai_project/` (or `--path DIRECTORY`) and saves its `project.json`; `project list` shows the projects saved as `*/project.json` under the current directory. An unknown template, an existing project name or an existing directory is reported as an error.

### From Python

```python
from codomyrmex.logistics.orchestration.project import ProjectType, get_project_manager

# The global manager (shared with get_orchestration_engine()); its projects_root
# is the current directory when it is first created. ProjectManager(projects_root)
# creates an independent one.
pm = get_project_manager()

project = pm.create_project(
    name="my_ai_project",
    type=ProjectType.AI_ANALYSIS,
    description="AI analysis of my codebase",
)
if project is None:
    raise RuntimeError("project not created; see the log for the reason")

print(f"Created project: {project.name}")
print(f"Path: {project.path}")
print(f"Metadata: {project.metadata_file}")  # <path>/project.json
```

`create_project` returns None (and logs why) if the name is already registered, the directory exists, or scaffolding failed; a partially created directory is removed. Pass `path=` to create the project elsewhere; it is then found by a `ProjectManager` whose `projects_root` is that directory's parent.

## Step 3: Execute Workflows for the Project

Workflows are registered with the `WorkflowManager` (see [Workflow Configuration Schema](./workflow-configuration-schema.md)), for example with `codomyrmex workflow create ai-analysis --template ai-analysis` in the same directory. Running one through the orchestration engine records the run in the project's metrics:

```python
from codomyrmex.logistics.orchestration.project import get_orchestration_engine

engine = get_orchestration_engine()

result = engine.execute_project_workflow("my_ai_project", "ai-analysis")

if result["success"]:
    print("Workflow completed successfully")
else:
    print(f"Workflow failed: {result['error']}")
```

The engine uses the global managers (`get_project_manager()`, `get_workflow_manager()`), which load from the current directory when first created. `execute_project_workflow` updates the metrics `workflow_executions`, `successful_workflow_executions`, `last_workflow`, `last_workflow_success` and `last_workflow_execution`.

## Step 4: Track Milestones, Metrics and Status

```python
from codomyrmex.logistics.orchestration.project import ProjectStatus

pm.add_project_milestone(
    "my_ai_project",
    "initial_analysis_complete",
    {"files_analyzed": 150},
)
pm.update_project_metrics("my_ai_project", {"success_rate": 0.95})
pm.update_project_status("my_ai_project", ProjectStatus.COMPLETED)
```

Each call returns False for an unknown project, sets `updated_at` and saves `project.json`. Values must be JSON-serialisable: a `TypeError` (or `ValueError` for NaN/infinity, `OSError` for a failed write) propagates and leaves the project unchanged.

After changing a `Project` object directly (for example `project.config`), save it explicitly:

```python
project = pm.get_project("my_ai_project")
project.config["analysis_depth"] = "full"
pm.save_project("my_ai_project")
```

## Project Management

### List Projects

```python
for project in pm.list_projects():
    print(project.name, project.status.value, project.path)
```

### Get Projects Summary

```python
summary = pm.get_projects_summary()

print(f"Total projects: {summary['total_projects']}")
print(f"By status: {summary['by_status']}")
print(f"By type: {summary['by_type']}")
print(f"Recent activity: {summary['recent_activity'][:5]}")
```

### Persistence

`project.json` holds `Project.to_dict()`:

```json
{
  "name": "my_ai_project",
  "path": "/work/my_ai_project",
  "type": "ai_analysis",
  "description": "AI analysis of my codebase",
  "status": "active",
  "config": {},
  "created_at": "2026-10-07T22:27:56.957872+00:00",
  "updated_at": "2026-10-07T22:27:56.957879+00:00",
  "owner": null,
  "version": "0.1.0",
  "metrics": {},
  "milestones": {}
}
```

`ProjectManager(projects_root)` registers every `<projects_root>/*/project.json` it can read with `Project.from_dict`; a file that is not valid JSON or not a valid project (missing field, unknown type or status, timestamp without a UTC offset) is logged and skipped. If a project directory was moved, its new location replaces the recorded `path`.

### Project File Structure

```text
my_ai_project/
├── README.md              # Generated project documentation
├── AGENTS.md              # Generated agent documentation
├── project.json           # Saved Project record
├── src/
│   ├── README.md
│   └── AGENTS.md
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

## Best Practices

1. **Type selection**: Choose the type that matches the project's purpose
2. **Naming**: Use descriptive project names
3. **Milestones**: Track progress with meaningful milestones
4. **Metrics**: Keep metric values JSON-serialisable
5. **Documentation**: Review and extend the generated documentation
6. **Location**: Keep projects in one parent directory so `project list` finds them

## Related Documentation

- [Project Template Schema](./project-template-schema.md)
- [Config-Driven Operations](./config-driven-operations.md)
- [API Specification](../../src/codomyrmex/logistics/orchestration/project/API_SPECIFICATION.md)

## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../../docs/README.md)
- **Home**: [Repository Root](../../README.md)
