# Codomyrmex Agents — src/codomyrmex/logistics/orchestration/project/templates

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose

Stores project template definitions in JSON format for the ProjectManager. These templates define reusable project structures including tasks, resources, workflows, and documentation templates for common project types.

## Active Components

- `web_application.json` - Template for web application projects
- `data_pipeline.json` - Template for data pipeline projects
- `ai_analysis.json` - Template for AI/ML analysis projects
- `doc_templates/` - Documentation generation templates (README, AGENTS.md formats)
- `SPEC.md` - Directory specification
- `README.md` - Directory documentation

## Template JSON Structure

### Standard Template Format
```json
{
  "name": "template_name",
  "type": "PROJECT_TYPE",
  "description": "Template description",
  "version": "1.0.0",
  "tasks": [
    {
      "name": "task_name",
      "module": "target_module",
      "action": "action_name",
      "dependencies": ["other_task"],
      "priority": "NORMAL",
      "parameters": {}
    }
  ],
  "resources": [
    {
      "type": "CPU",
      "required": 2,
      "preferred": 4
    }
  ],
  "workflows": [
    {
      "name": "workflow_name",
      "steps": ["task1", "task2"]
    }
  ],
  "documentation": {
    "readme_template": "path/to/template",
    "include_agents_md": true
  }
}
```

### Available Templates
- **web_application.json**: Frontend/backend setup, API endpoints, database, deployment
- **data_pipeline.json**: Data ingestion, transformation, validation, storage, monitoring
- **ai_analysis.json**: Model training, evaluation, inference, reporting workflows

### doc_templates/ Subdirectory
- README.md templates with placeholders for project-specific content
- AGENTS.md templates for automated documentation generation
- Markdown templates for various documentation needs

## Operating Contracts

- Templates are validated against JSON schema on load
- Placeholders use `{{variable_name}}` syntax for substitution
- Task names must be unique within a template
- Dependencies must reference existing tasks
- Resource requirements validated against ResourceType enum

## Signposting

- **Consumed By**: `project_manager.py` (ProjectManager)
- **Parent Directory**: [project](../README.md) - Parent module documentation
- **Related Modules**:
  - `documentation_generator.py` - Uses doc_templates for generation
  - `workflow_manager.py` - Consumes workflow definitions
- **Project Root**: [../../../../../../README.md](../../../../../../README.md) - Main project documentation
