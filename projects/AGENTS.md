# Codomyrmex Agents — projects

## Purpose
Workspace for composite agent-driven project scaffolds with rich template expressivity and automatic nested documentation generation.

## Active Components
- **Project Templates**: Rich, expressive templates with documentation configuration
- **Documentation Generator**: Automatic generation of README.md and AGENTS.md files for projects and nested directories
- **Template System**: Support for variable substitution, nested documentation, and template inheritance
- **Project Manager Integration**: Seamless integration with project creation workflow

## Operating Contracts
- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.
- Generate nested documentation automatically when projects are created from templates.
- Maintain hierarchical cross-linking between parent and child directory documentation.
- Support template variable substitution and customization.

## Template Documentation Features

### Automatic Documentation Generation
- Projects created from templates automatically generate README.md and AGENTS.md files
- Nested directories specified in template configuration receive their own documentation
- Cross-linking between parent and child directories for easy navigation

### Template Expressivity
- Variable substitution using `{{variable}}` syntax
- Template inheritance from base templates
- Template-specific overrides for custom behavior
- Support for nested documentation configuration

### Documentation Structure
Each project includes:
- Root-level README.md and AGENTS.md
- Nested README.md and AGENTS.md for each configured directory
- Automatic cross-references between parent and child directories

## Navigation Links
- **📚 Projects Overview**: [README.md](README.md) - Projects workspace documentation
- **🏠 Project Root**: [../README.md](../README.md) - Main project README
- **📖 Documentation Hub**: [../docs/README.md](../docs/README.md) - Complete documentation structure
- **🎯 Project Orchestration**: [../src/codomyrmex/project_orchestration/README.md](../src/codomyrmex/project_orchestration/README.md) - Project orchestration module
