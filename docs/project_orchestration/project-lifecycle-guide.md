# Project Lifecycle Guide

Complete guide for managing projects from template selection through creation, execution, monitoring, and completion.

## Overview

Projects in Codomyrmex represent organized work units with defined structure, workflows, and configuration. This guide covers the complete project lifecycle from template selection to project completion or archival.

## Step 1: Select and Customize Template

### List Available Templates

```python
from codomyrmex.project_orchestration import get_project_manager

pm = get_project_manager()

# List all available templates
templates = pm.list_templates()
print(f"Available templates: {templates}")
# Output: ['ai_analysis', 'web_application', 'data_pipeline', ...]
```

### Get Template Details

```python
# Get template information
template = pm.get_template("ai_analysis")

if template:
    print(f"Template: {template.name}")
    print(f"Type: {template.type.value}")
    print(f"Description: {template.description}")
    print(f"Required modules: {template.required_modules}")
    print(f"Workflows: {template.workflows}")
    print(f"Directory structure: {template.directory_structure}")
```

### Template Types

Available template types:
- `ai_analysis` - AI-powered code analysis
- `web_application` - Full-stack web applications
- `data_pipeline` - Data processing pipelines
- `ml_model` - Machine learning projects
- `documentation` - Documentation projects
- `research` - Research projects
- `custom` - Custom project types

## Step 2: Create Project with Configuration

### Basic Project Creation

```python
# Create project from template
project = pm.create_project(
    name="my_ai_project",
    template_name="ai_analysis",
    description="AI analysis of my codebase",
    author="Developer Name"
)

print(f"Created project: {project.name}")
print(f"Path: {project.path}")
print(f"Type: {project.type.value}")
```

### Custom Project Path

```python
# Create project in custom location
project = pm.create_project(
    name="custom_project",
    template_name="ai_analysis",
    path="/path/to/custom/location",
    description="Custom location project"
)
```

### Custom Project (No Template)

```python
# Create project without template
project = pm.create_project(
    name="custom_project",
    description="Custom project without template",
    author="Developer"
)
# Project type will be CUSTOM
```

### Project with Custom Configuration

```python
# Create project and override default config
project = pm.create_project(
    name="configured_project",
    template_name="ai_analysis",
    description="Project with custom configuration",
    # Additional kwargs are passed to project creation
    # Default config from template can be overridden later
)
```

## Step 3: Execute Project Workflows

### List Available Workflows

```python
# Get project
project = pm.get_project("my_ai_project")

if project:
    print(f"Available workflows: {project.workflows}")
    # Output: ['ai-analysis', 'build-and-test']
```

### Execute Workflow

```python
# Execute a workflow for the project
result = pm.execute_project_workflow(
    project_name="my_ai_project",
    workflow_name="ai-analysis",
    code_path="./src",
    output_path="./reports",
    ai_provider="openai"
)

if result['success']:
    print(f"Workflow completed successfully")
    print(f"Results: {result.get('results', {})}")
else:
    print(f"Workflow failed: {result.get('error', 'Unknown error')}")
```

### Execute via OrchestrationEngine

```python
from codomyrmex.project_orchestration import get_orchestration_engine

engine = get_orchestration_engine()

# Execute with session management
result = engine.execute_project_workflow(
    project_name="my_ai_project",
    workflow_name="ai-analysis",
    code_path="./src"
)
```

## Step 4: Track Milestones and Metrics

### Add Milestone

```python
# Add milestone to track progress
pm.add_project_milestone(
    name="my_ai_project",
    milestone_name="initial_analysis_complete",
    milestone_data={
        "quality_score": 8.5,
        "insights_generated": 23,
        "files_analyzed": 150
    }
)
```

### Update Metrics

```python
# Update project metrics
pm.update_project_metrics(
    name="my_ai_project",
    metrics={
        "total_executions": 10,
        "success_rate": 0.95,
        "average_execution_time": 45.2,
        "last_execution": "2025-01-15T10:30:00Z"
    }
)
```

### Get Project Status

```python
# Get detailed project status
status = pm.get_project_status("my_ai_project")

if status:
    print(f"Project: {status['name']}")
    print(f"Status: {status['status']}")
    print(f"Version: {status['version']}")
    print(f"Workflows: {status['workflows']}")
    print(f"Active workflows: {status['active_workflows']}")
    print(f"Milestones: {list(status['milestones'].keys())}")
    print(f"Metrics: {status['metrics']}")
```

## Step 5: Archive or Complete Project

### Complete Project

```python
# Mark project as completed
project = pm.get_project("my_ai_project")
if project:
    project.status = ProjectStatus.COMPLETED
    project.save()
    
    # Add final milestone
    pm.add_project_milestone(
        "my_ai_project",
        "project_completed",
        {
            "completion_date": datetime.now(timezone.utc).isoformat(),
            "final_metrics": project.metrics
        }
    )
```

### Archive Project

```python
# Archive project (creates tar.gz archive)
success = pm.archive_project(
    name="my_ai_project",
    archive_path="./archives/my_ai_project.tar.gz"
)

if success:
    print("Project archived successfully")
```

### Delete Project

```python
# Delete project (remove from manager)
success = pm.delete_project("my_ai_project", remove_files=False)

# Or delete project and remove files
success = pm.delete_project("my_ai_project", remove_files=True)
```

## Project Management

### List Projects

```python
# List all projects
projects = pm.list_projects()
print(f"Projects: {projects}")
```

### Get Projects Summary

```python
# Get summary of all projects
summary = pm.get_projects_summary()

print(f"Total projects: {summary['total_projects']}")
print(f"By status: {summary['by_status']}")
print(f"By type: {summary['by_type']}")
print(f"Recent activity: {summary['recent_activity'][:5]}")
```

### Project File Structure

Projects created from templates have the following structure:

```
my_ai_project/
├── README.md              # Auto-generated project documentation
├── AGENTS.md              # Auto-generated agent configuration
├── src/                   # Source code directory
│   ├── README.md          # Nested documentation
│   └── AGENTS.md          # Nested agent config
├── data/                  # Data directory
│   ├── README.md
│   └── AGENTS.md
├── output/                # Output directory
│   ├── README.md
│   └── AGENTS.md
├── reports/               # Reports directory
│   ├── README.md
│   └── AGENTS.md
├── config/                # Configuration directory
│   ├── README.md
│   └── AGENTS.md
└── .codomyrmex/          # Project metadata
    └── project.json       # Project configuration
```

## Complete Example

```python
from codomyrmex.project_orchestration import (
    get_project_manager,
    ProjectStatus
)
from datetime import datetime, timezone

# Initialize project manager
pm = get_project_manager()

# 1. List templates
templates = pm.list_templates()
print(f"Available templates: {templates}")

# 2. Create project
project = pm.create_project(
    name="codebase_analysis",
    template_name="ai_analysis",
    description="Comprehensive analysis of codebase quality",
    author="Development Team"
)

print(f"Created project: {project.name} at {project.path}")

# 3. Execute workflow
result = pm.execute_project_workflow(
    project_name="codebase_analysis",
    workflow_name="ai-analysis",
    code_path="./src",
    output_path="./reports",
    ai_provider="openai"
)

if result['success']:
    # 4. Track milestone
    pm.add_project_milestone(
        "codebase_analysis",
        "initial_analysis_complete",
        {
            "quality_score": 8.5,
            "files_analyzed": 250,
            "insights_generated": 45
        }
    )
    
    # 5. Update metrics
    pm.update_project_metrics(
        "codebase_analysis",
        {
            "workflow_executions": 1,
            "success_rate": 1.0,
            "last_execution": datetime.now(timezone.utc).isoformat()
        }
    )
    
    # 6. Get status
    status = pm.get_project_status("codebase_analysis")
    print(f"Project status: {status}")
    
    # 7. Complete project
    project = pm.get_project("codebase_analysis")
    if project:
        project.status = ProjectStatus.COMPLETED
        project.save()
        print("Project completed")
```

## Best Practices

1. **Template Selection**: Choose templates that match your project type
2. **Naming**: Use descriptive project names
3. **Milestones**: Track progress with meaningful milestones
4. **Metrics**: Update metrics regularly for monitoring
5. **Documentation**: Review auto-generated documentation
6. **Workflows**: Execute workflows appropriate for project stage
7. **Completion**: Archive completed projects for reference

## Related Documentation

- [Project Template Schema](./project-template-schema.md)
- [Config-Driven Operations](./config-driven-operations.md)
- [API Specification](../../src/codomyrmex/project_orchestration/API_SPECIFICATION.md)

