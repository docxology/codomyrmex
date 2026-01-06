# Project Template Schema

This document describes the JSON schema for project templates, variable substitution syntax, nested documentation configuration, and provides examples for all project types.

## Overview

Project templates define the structure, configuration, and workflows for creating new Codomyrmex projects. Templates are stored as JSON files in `src/codomyrmex/project_orchestration/templates/` and are automatically loaded by the ProjectManager.

## JSON Schema

### Root Object

```json
{
  "name": "string (required)",
  "type": "string (required)",
  "description": "string",
  "version": "string",
  "directory_structure": [],
  "template_files": {},
  "workflows": [],
  "required_modules": [],
  "optional_modules": [],
  "default_config": {},
  "documentation_config": {},
  "author": "string",
  "created_at": "ISO 8601 datetime"
}
```

### Field Descriptions

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `name` | string | Yes | - | Unique template identifier |
| `type` | string | Yes | - | Project type (see ProjectType enum) |
| `description` | string | No | `""` | Template description |
| `version` | string | No | `"1.0"` | Template version |
| `directory_structure` | array | No | `[]` | List of directories to create |
| `template_files` | object | No | `{}` | File mappings (src → dest) |
| `workflows` | array | No | `[]` | Default workflow names |
| `required_modules` | array | No | `[]` | Required Codomyrmex modules |
| `optional_modules` | array | No | `[]` | Optional Codomyrmex modules |
| `default_config` | object | No | `{}` | Default project configuration |
| `documentation_config` | object | No | `{}` | Documentation generation config |
| `author` | string | No | `""` | Template author |
| `created_at` | string | No | Current time | Creation timestamp (ISO 8601) |

### Project Types

The `type` field must be one of:
- `ai_analysis` - AI-powered code analysis projects
- `web_application` - Full-stack web applications
- `data_pipeline` - Data processing pipelines
- `ml_model` - Machine learning model projects
- `documentation` - Documentation projects
- `research` - Research projects
- `custom` - Custom project types

## Complete Template Example

```json
{
  "name": "ai_analysis",
  "type": "ai_analysis",
  "description": "AI-powered code analysis and insights project",
  "version": "1.0",
  "directory_structure": [
    "src/",
    "data/",
    "output/",
    "reports/",
    "config/",
    ".codomyrmex/"
  ],
  "template_files": {},
  "workflows": [
    "ai-analysis",
    "build-and-test"
  ],
  "required_modules": [
    "ai_code_editing",
    "static_analysis",
    "data_visualization"
  ],
  "optional_modules": [
    "git_operations",
    "documentation"
  ],
  "default_config": {
    "analysis": {
      "include_patterns": ["*.py", "*.js", "*.ts"],
      "exclude_patterns": ["*/node_modules/*", "*/__pycache__/*"],
      "max_file_size": "1MB"
    },
    "ai": {
      "provider": "openai",
      "model": "gpt-3.5-turbo"
    },
    "output": {
      "formats": ["json", "html", "pdf"],
      "include_visualizations": true
    }
  },
  "documentation_config": {
    "nested_docs": ["src/", "config/", "data/", "output/", "reports/"],
    "doc_links": {
      "enabled": true,
      "parent_link": true,
      "child_links": true
    }
  },
  "author": "",
  "created_at": "2025-09-16T13:22:09.907080+00:00"
}
```

## Variable Substitution

Templates support variable substitution in generated files and documentation. The following variables are available:

### Available Variables

- `{{project_name}}` - Project name
- `{{project_type}}` - Project type
- `{{description}}` - Project description
- `{{version}}` - Project version
- `{{author}}` - Project author
- `{{created_at}}` - Creation timestamp (ISO 8601)

### Variable Usage

Variables are substituted in:
1. **Template Files**: When copying template files, variables in file contents are replaced
2. **Documentation**: Variables in README.md and AGENTS.md templates are replaced
3. **Configuration**: Variables in default_config can reference project metadata

### Example with Variables

```json
{
  "name": "custom_template",
  "type": "custom",
  "description": "Template for {{project_name}}",
  "default_config": {
    "project": {
      "name": "{{project_name}}",
      "type": "{{project_type}}",
      "version": "{{version}}",
      "created": "{{created_at}}"
    }
  }
}
```

## Directory Structure

The `directory_structure` array defines which directories should be created when a project is instantiated from the template.

### Example

```json
{
  "directory_structure": [
    "src/",
    "tests/",
    "docs/",
    "config/",
    "data/raw/",
    "data/processed/",
    "output/",
    ".codomyrmex/"
  ]
}
```

### Special Directories

- `.codomyrmex/` - Always created for project metadata and configuration
- Other directories can be customized based on project needs

## Documentation Configuration

The `documentation_config` object controls automatic documentation generation:

```json
{
  "documentation_config": {
    "nested_docs": ["src/", "config/", "data/"],
    "doc_links": {
      "enabled": true,
      "parent_link": true,
      "child_links": true
    }
  }
}
```

### Nested Documentation

The `nested_docs` array specifies which directories should receive auto-generated README.md and AGENTS.md files:

- Each directory listed gets `README.md` and `AGENTS.md`
- Documentation includes cross-links to parent and child directories
- Variables are substituted in all documentation

### Documentation Links

The `doc_links` object controls cross-linking:

- `enabled`: Enable/disable cross-linking (default: true)
- `parent_link`: Include link to parent directory in nested docs (default: true)
- `child_links`: Include links to child directories in parent docs (default: true)

## Template Files

The `template_files` object maps source file patterns to destination paths:

```json
{
  "template_files": {
    "templates/*.py": "src/",
    "templates/config.yaml": "config/"
  }
}
```

### File Mapping Rules

- Source patterns use glob syntax
- Destination paths are relative to project root
- Files are copied from `templates/{template_name}/` directory
- Variables in file contents are substituted during copy

## Workflows

The `workflows` array specifies which workflows are available for projects created from this template:

```json
{
  "workflows": [
    "ai-analysis",
    "build-and-test",
    "deploy"
  ]
}
```

These workflows can be executed via:
```python
project_manager.execute_project_workflow(project_name, "ai-analysis")
```

## Module Dependencies

### Required Modules

Modules listed in `required_modules` are essential for the project:

```json
{
  "required_modules": [
    "ai_code_editing",
    "static_analysis"
  ]
}
```

### Optional Modules

Modules listed in `optional_modules` are recommended but not required:

```json
{
  "optional_modules": [
    "git_operations",
    "documentation"
  ]
}
```

## Default Configuration

The `default_config` object provides default configuration values for the project:

```json
{
  "default_config": {
    "analysis": {
      "include_patterns": ["*.py"],
      "exclude_patterns": ["*/__pycache__/*"]
    },
    "ai": {
      "provider": "openai",
      "model": "gpt-3.5-turbo"
    }
  }
}
```

This configuration is:
- Stored in the project's `.codomyrmex/project.json`
- Accessible via `project.config`
- Can be overridden per-project
- Supports variable substitution

## Template Examples by Type

### AI Analysis Template

```json
{
  "name": "ai_analysis",
  "type": "ai_analysis",
  "description": "AI-powered code analysis and insights project",
  "directory_structure": [
    "src/",
    "data/",
    "output/",
    "reports/",
    "config/",
    ".codomyrmex/"
  ],
  "workflows": ["ai-analysis"],
  "required_modules": ["ai_code_editing", "static_analysis"],
  "default_config": {
    "ai": {"provider": "openai", "model": "gpt-3.5-turbo"},
    "analysis": {"include_patterns": ["*.py", "*.js"]}
  }
}
```

### Data Pipeline Template

```json
{
  "name": "data_pipeline",
  "type": "data_pipeline",
  "description": "Data processing and analysis pipeline",
  "directory_structure": [
    "pipelines/",
    "data/raw/",
    "data/processed/",
    "data/output/",
    "notebooks/",
    "config/",
    "tests/",
    ".codomyrmex/"
  ],
  "workflows": ["data-processing", "visualization"],
  "required_modules": ["data_visualization", "code"],
  "default_config": {
    "data": {
      "input_formats": ["csv", "json"],
      "output_formats": ["csv", "json"]
    },
    "processing": {
      "parallel": true,
      "batch_size": 1000
    }
  }
}
```

### Web Application Template

```json
{
  "name": "web_application",
  "type": "web_application",
  "description": "Full-stack web application",
  "directory_structure": [
    "frontend/",
    "backend/",
    "database/",
    "docs/",
    "tests/",
    "deploy/",
    ".codomyrmex/"
  ],
  "workflows": ["build-and-test", "deploy"],
  "required_modules": ["build_synthesis", "code"],
  "default_config": {
    "frontend": {"framework": "react", "build_tool": "vite"},
    "backend": {"framework": "fastapi", "database": "postgresql"}
  }
}
```

## Creating Custom Templates

### Step 1: Define Template Structure

Create a JSON file in `src/codomyrmex/project_orchestration/templates/`:

```json
{
  "name": "my_custom_template",
  "type": "custom",
  "description": "My custom project template",
  "directory_structure": ["src/", "tests/", ".codomyrmex/"],
  "workflows": ["custom-workflow"],
  "required_modules": ["static_analysis"]
}
```

### Step 2: Add Template Files (Optional)

Create a directory `src/codomyrmex/project_orchestration/templates/my_custom_template/` and add files that should be copied:

```
templates/my_custom_template/
├── src/
│   └── main.py.template
└── config/
    └── config.yaml.template
```

### Step 3: Use the Template

```python
from codomyrmex.project_orchestration import get_project_manager

pm = get_project_manager()
project = pm.create_project(
    name="my_project",
    template_name="my_custom_template",
    description="My custom project"
)
```

## Validation

### Required Fields

- `name`: Must be unique, non-empty string
- `type`: Must be a valid ProjectType value

### Template Loading

Templates are validated when loaded:
- Invalid JSON causes loading to fail
- Missing required fields cause warnings
- Invalid project types cause errors

## Best Practices

1. **Naming**: Use descriptive template names that indicate the project type
2. **Structure**: Define a clear directory structure that matches project needs
3. **Documentation**: Enable nested documentation for better project organization
4. **Configuration**: Provide sensible defaults in `default_config`
5. **Modules**: Only list truly required modules in `required_modules`
6. **Variables**: Use variable substitution to avoid hardcoding project-specific values

## Related Documentation

- [Project Lifecycle Guide](./project-lifecycle-guide.md)
- [Config-Driven Operations](./config-driven-operations.md)
- [API Specification](../../src/codomyrmex/project_orchestration/API_SPECIFICATION.md)

