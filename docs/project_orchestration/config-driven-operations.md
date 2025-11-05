# Config-Driven Operations Guide

Comprehensive guide for configuration-driven operations covering workflows, projects, and resources across the Codomyrmex orchestration system.

## Overview

Codomyrmex supports fully configuration-driven operations, allowing you to define workflows, projects, and resource configurations in JSON files that are loaded and executed automatically. This guide covers all aspects of config-driven operations.

## Configuration File Locations

### Workflow Configurations

- **Location**: `.codomyrmex/workflows/*.json`
- **Auto-loaded**: Yes, when WorkflowManager initializes
- **Format**: JSON workflow definitions

### Project Templates

- **Location**: `src/codomyrmex/project_orchestration/templates/*.json`
- **Auto-loaded**: Yes, when ProjectManager initializes
- **Format**: JSON template definitions

### Resource Configuration

- **Location**: `resources.json` (project root or configured path)
- **Auto-loaded**: Yes, when ResourceManager initializes
- **Format**: JSON resource definitions

## Workflow Configuration

### Creating Workflow Configurations

Create a JSON file in `.codomyrmex/workflows/`:

```json
{
  "name": "my_custom_workflow",
  "steps": [
    {
      "name": "step1",
      "module": "static_analysis",
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

### Loading Workflows

Workflows are automatically loaded:

```python
from codomyrmex.project_orchestration import get_workflow_manager

# Workflows are loaded automatically
manager = get_workflow_manager()

# List loaded workflows
workflows = manager.list_workflows()
print(f"Loaded workflows: {list(workflows.keys())}")
```

### Executing Configured Workflows

```python
import asyncio
from codomyrmex.project_orchestration import get_workflow_manager

async def main():
    manager = get_workflow_manager()
    
    # Execute workflow from configuration
    execution = await manager.execute_workflow(
        "my_custom_workflow",
        parameters={
            "custom_param": "value"
        }
    )
    
    if execution.status == WorkflowStatus.COMPLETED:
        print("Workflow completed")
        for step_name, result in execution.results.items():
            print(f"{step_name}: {result}")

asyncio.run(main())
```

## Project Template Configuration

### Creating Project Templates

Create a JSON file in `src/codomyrmex/project_orchestration/templates/`:

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

Templates are automatically loaded and available:

```python
from codomyrmex.project_orchestration import get_project_manager

pm = get_project_manager()

# Templates are loaded automatically
templates = pm.list_templates()
print(f"Available templates: {templates}")

# Create project from template
project = pm.create_project(
    name="my_project",
    template_name="my_custom_template",
    description="Project from custom template"
)
```

## Resource Configuration

### Creating Resource Configurations

Create or update `resources.json`:

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

Resources are automatically loaded:

```python
from codomyrmex.project_orchestration import get_resource_manager

# Resources are loaded automatically from resources.json
rm = get_resource_manager()

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
from codomyrmex.project_orchestration import OrchestrationEngine

config = {
    "max_workers": 8,
    "workflows_dir": "./workflows",
    "projects_dir": "./projects",
    "templates_dir": "./templates",
    "resource_config": "./resources.json",
    "performance_monitoring": True,
    "session_timeout": 3600,
    "cleanup_interval": 300
}

engine = OrchestrationEngine(config=config)
```

### Environment-Based Configuration

```python
import os

# Load configuration from environment
config = {
    "max_workers": int(os.getenv("CODOMYRMEX_MAX_WORKERS", "4")),
    "workflows_dir": os.getenv("CODOMYRMEX_WORKFLOWS_DIR", ".codomyrmex/workflows"),
    "projects_dir": os.getenv("CODOMYRMEX_PROJECTS_DIR", "projects"),
    "templates_dir": os.getenv("CODOMYRMEX_TEMPLATES_DIR", None),  # Use default
    "resource_config": os.getenv("CODOMYRMEX_RESOURCE_CONFIG", "resources.json"),
    "performance_monitoring": os.getenv("CODOMYRMEX_PERFORMANCE_MONITORING", "true").lower() == "true"
}

engine = OrchestrationEngine(config=config)
```

## Configuration Validation

### Workflow Validation

```python
from codomyrmex.project_orchestration import WorkflowManager, WorkflowStep

manager = WorkflowManager()

# Validate workflow when creating
steps = [
    WorkflowStep(name="step1", module="module1", action="action1"),
    WorkflowStep(name="step2", module="module2", action="action2", dependencies=["step1"])
]

# Validation happens during create_workflow
success = manager.create_workflow("valid_workflow", steps)
# Returns False if validation fails, logs errors
```

### Template Validation

Templates are validated when loaded:

```python
# Invalid templates are skipped with error logging
# Valid templates are loaded successfully
pm = get_project_manager()
templates = pm.list_templates()  # Only valid templates
```

### Resource Validation

Resources are validated when loaded:

```python
# Invalid resources are skipped with error logging
# Valid resources are loaded successfully
rm = get_resource_manager()
resources = rm.list_resources()  # Only valid resources
```

## Complete Config-Driven Example

### 1. Create Workflow Configuration

`.codomyrmex/workflows/data_analysis.json`:
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

### 2. Create Project Template

`src/codomyrmex/project_orchestration/templates/data_project.json`:
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
import asyncio
from codomyrmex.project_orchestration import (
    get_orchestration_engine,
    get_project_manager
)

async def main():
    # Create project from template
    pm = get_project_manager()
    project = pm.create_project(
        name="analysis_project",
        template_name="data_project"
    )
    
    # Execute workflow (automatically loaded from config)
    engine = get_orchestration_engine()
    result = engine.execute_workflow(
        "data_analysis",
        input_file="./data/input.csv",
        output_path="./output/result.png"
    )
    
    if result['success']:
        print("Analysis completed")

asyncio.run(main())
```

## Best Practices

1. **Version Control**: Keep configuration files in version control
2. **Validation**: Validate configurations before deployment
3. **Documentation**: Document configuration options and examples
4. **Environment Separation**: Use environment-specific configs for different deployments
5. **Parameter Substitution**: Use parameter substitution for flexibility
6. **Resource Management**: Configure resources based on actual system capacity
7. **Error Handling**: Handle configuration loading errors gracefully

## Related Documentation

- [Workflow Configuration Schema](./workflow-configuration-schema.md)
- [Project Template Schema](./project-template-schema.md)
- [Resource Configuration](./resource-configuration.md)
- [API Specification](../src/codomyrmex/project_orchestration/API_SPECIFICATION.md)

