# projects

**Version**: v0.2.0 | **Status**: Active | **Last Updated**: November 2025

## Overview

Workspace for composite agent-driven project scaffolds with rich template expressivity and automatic nested documentation generation.

## Core Capabilities

### Primary Functions
- **Modular Architecture**: Self-contained module with clear boundaries and responsibilities
- **Agent Integration**: Seamlessly integrates with Codomyrmex agent ecosystem
- **Rich Templates**: Expressive project templates with variable substitution and nested documentation
- **Automatic Documentation**: Generates README.md and AGENTS.md files for projects and nested directories
- **Template Inheritance**: Support for template customization and inheritance
- **Comprehensive Testing**: Full test coverage with unit, integration, and performance tests

## Architecture

```
projects/
├── README.md              # This file
├── AGENTS.md              # Agent configuration
└── test_project/         # Example project
    ├── README.md          # Project root documentation (auto-generated)
    ├── AGENTS.md          # Project root agents (auto-generated)
    ├── src/
    │   ├── README.md      # Nested documentation (auto-generated)
    │   └── AGENTS.md      # Nested agents (auto-generated)
    ├── config/
    │   ├── README.md      # Nested documentation (auto-generated)
    │   └── AGENTS.md      # Nested agents (auto-generated)
    └── ...                # Other directories with nested docs
```

## Key Components

### Active Components
- **Project Templates**: Rich, expressive templates with documentation configuration
- **Documentation Generator**: Automatic generation of README and AGENTS files
- **Template System**: Support for variable substitution and nested structure
- **Project Manager Integration**: Seamless integration with project creation workflow

### Template Features

#### Rich Template Expressivity
Templates support:
- **Variable Substitution**: Use `{{variable}}` syntax in templates
- **Nested Documentation**: Automatic README/AGENTS generation for subdirectories
- **Cross-linking**: Hierarchical navigation between parent and child directories
- **Template Inheritance**: Base templates with template-specific overrides

#### Available Variables
- `{{project_name}}` - Project name
- `{{project_type}}` - Project type (ai_analysis, data_pipeline, etc.)
- `{{description}}` - Project description
- `{{version}}` - Project version
- `{{author}}` - Project author
- `{{created_at}}` - Creation timestamp

#### Template Configuration
Templates can include a `documentation_config` section:
```json
{
  "documentation_config": {
    "nested_docs": ["src/", "config/", "data/", "output/", "reports/"],
    "doc_links": {
      "enabled": true,
      "parent_link": true,
      "child_links": true
    }
  }
}
```

## Operating Contracts

- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.

## Integration Points

### Related Modules
No related modules specified

## Usage Examples

### Creating a Project with Automatic Documentation

```python
from codomyrmex.project_orchestration import get_project_manager

# Get project manager
project_manager = get_project_manager()

# Create project from template (documentation is automatically generated)
project = project_manager.create_project(
    name="my_ai_project",
    template_name="ai_analysis",
    description="AI-powered code analysis project",
    author="Developer Name"
)

# Project now has:
# - README.md at project root
# - AGENTS.md at project root
# - README.md and AGENTS.md in each nested directory (src/, config/, data/, etc.)
```

### Manual Documentation Generation

```python
from pathlib import Path
from codomyrmex.project_orchestration.documentation_generator import DocumentationGenerator

# Initialize generator
generator = DocumentationGenerator()

# Generate documentation for existing project
project_path = Path("projects/my_project")
generator.generate_all_documentation(
    project_path=project_path,
    project_name="my_project",
    project_type="ai_analysis",
    description="My project description",
    version="1.0.0",
    author="Developer Name",
    created_at="2025-11-05T12:00:00+00:00",
    nested_dirs=["src", "config", "data", "output", "reports"],
    template="ai_analysis",
    doc_links={"enabled": True, "parent_link": True, "child_links": True}
)
```

### Template Structure Example

```python
# Template JSON structure
{
  "name": "ai_analysis",
  "type": "ai_analysis",
  "description": "AI-powered code analysis and insights project",
  "directory_structure": ["src/", "config/", "data/", "output/", "reports/"],
  "documentation_config": {
    "nested_docs": ["src/", "config/", "data/", "output/", "reports/"],
    "doc_links": {
      "enabled": true,
      "parent_link": true,
      "child_links": true
    }
  }
}
```

## Quality Assurance

The module includes comprehensive testing to ensure:
- **Reliability**: Consistent operation across different environments
- **Performance**: Optimized execution with monitoring and metrics
- **Security**: Secure by design with proper input validation
- **Maintainability**: Clean code structure with comprehensive documentation

## Development Guidelines

### Code Structure
- Follow project coding standards and `.cursorrules`
- Implement comprehensive error handling
- Include proper logging and telemetry
- Maintain backward compatibility

### Testing Requirements
- Unit tests for all public methods
- Integration tests for module interactions
- Performance benchmarks where applicable
- Security testing for sensitive operations

## Contributing

When contributing to this module:
1. Follow established patterns and conventions
2. Add comprehensive tests for new features
3. Update documentation for API changes
4. Ensure all tests pass before submitting
5. Consider impact on related modules

## Nested Documentation Structure

Each project created from a template automatically includes:

1. **Root Documentation**:
   - `README.md` - Project overview, capabilities, and usage
   - `AGENTS.md` - Agent configuration and active components

2. **Nested Documentation**:
   - Each directory specified in `nested_docs` gets:
     - `README.md` - Directory-specific purpose and structure
     - `AGENTS.md` - Directory-specific agent configuration
   - Automatic cross-linking between parent and child directories

### Example Nested Structure

```
my_project/
├── README.md              # Project root documentation
├── AGENTS.md              # Project root agents
├── src/
│   ├── README.md          # Source code directory docs
│   └── AGENTS.md          # Source code directory agents
│   └── (links to parent)
├── config/
│   ├── README.md          # Configuration directory docs
│   └── AGENTS.md          # Configuration directory agents
│   └── (links to parent)
└── ...
```

## Template Customization

Templates support customization through:

1. **Template Files**: Place custom template files in `templates/doc_templates/`
   - `README.template.md` - Base README template
   - `AGENTS.template.md` - Base AGENTS template
   - `README.nested.template.md` - Nested README template
   - `AGENTS.nested.template.md` - Nested AGENTS template

2. **Template-Specific Overrides**: Create template-specific templates:
   - `{template_name}_README.template.md`
   - `{template_name}_AGENTS.template.md`
   - `{template_name}_README.nested.template.md`
   - `{template_name}_AGENTS.nested.template.md`

3. **Variable Expansion**: All templates support variable substitution using `{{variable}}` syntax

## Related Documentation

- **AGENTS.md**: Detailed agent configuration and purpose
- **Template System**: See `src/codomyrmex/project_orchestration/templates/`
- **Documentation Generator**: See `src/codomyrmex/project_orchestration/documentation_generator.py`
- **Project Manager**: See `src/codomyrmex/project_orchestration/project_manager.py`
- **Example Project**: See `test_project/` for a complete example with nested documentation
- **Project Template Schema**: [Complete template schema documentation](../docs/project_orchestration/project-template-schema.md)
- **Project Lifecycle Guide**: [Complete project lifecycle management guide](../docs/project_orchestration/project-lifecycle-guide.md)
- **Config-Driven Operations**: [Configuration-driven project operations](../docs/project_orchestration/config-driven-operations.md)
