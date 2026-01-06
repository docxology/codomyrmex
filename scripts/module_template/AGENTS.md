# Codomyrmex Agents — scripts/module_template

## Signposting
- **Parent**: [Scripts](../AGENTS.md)
- **Self**: [Agents](AGENTS.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [Functional Spec](SPEC.md)
    - [Human Readme](README.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: December 2025

## Purpose

Module template automation scripts providing command-line interfaces for creating new Codomyrmex modules with standardized structure and scaffolding. This script module enables rapid module development following established patterns.

The module_template scripts serve as the primary interface for developers creating new modules within the Codomyrmex ecosystem.

## Module Overview

### Key Capabilities
- **Module Scaffolding**: Automated creation of module directory structure
- **Template Application**: Apply standardized templates for different module types
- **Configuration Setup**: Generate appropriate configuration files
- **Documentation Templates**: Create documentation scaffolding
- **Testing Framework**: Set up testing structure and fixtures

### Key Features
- Command-line interface with argument parsing
- Multiple module templates (core, service, specialized, etc.)
- Integration with core module system
- Validation of generated modules
- Template customization capabilities

## Function Signatures

### Core CLI Functions

```python
def main() -> None
```

Main CLI entry point for the module template orchestrator.

**Command-line Usage:**
```bash
python orchestrate.py [command] [options]
```

**Available Commands:**
- `info` - Display available module templates and information

**Global Options:**
- `--verbose, -v` - Enable verbose output
- `--template-dir, -t` - Path to template directory

```python
def handle_info(args) -> None
```

Handle information display commands from CLI arguments.

**Parameters:**
- `args` - Parsed command-line arguments containing:
  - `template_type` (str, optional): Filter templates by type
  - `show_details` (bool, optional): Show detailed template information. Defaults to False

**Returns:** None (displays module template information)

## Active Components

### Core Implementation
- `__init__.py` – Module initialization and public API exports
- `orchestrate.py` – Main CLI orchestrator script

### Template Assets
- `templates/` – Module template files and structures
- `config_templates/` – Configuration file templates
- `test_templates/` – Testing framework templates

### Documentation
- `README.md` – Script usage and overview
- `AGENTS.md` – This coordination document

### Supporting Files
- Integration with `_orchestrator_utils.py` for shared utilities


### Additional Files
- `SPEC.md` – Spec Md

## Operating Contracts

### Universal Script Protocols

All scripts in this module must:

1. **CLI Standards**: Follow consistent command-line argument patterns
2. **Error Handling**: Provide clear error messages and exit codes
3. **Template Validation**: Ensure generated modules follow standards
4. **Documentation**: Include clear usage instructions for templates
5. **Maintainability**: Keep templates current with platform evolution

### Module-Specific Guidelines

#### Template Creation
- Support multiple module types and complexity levels
- Include comprehensive file structure scaffolding
- Provide appropriate configuration templates
- Include testing framework setup

#### Module Generation
- Validate module names and paths
- Create appropriate directory structures
- Apply correct permissions and ownership
- Generate necessary configuration files

#### Template Maintenance
- Keep templates synchronized with current module standards
- Update templates when new patterns are established
- Document template usage and customization
- Provide migration paths for template updates

## Navigation Links
- **Human Documentation**: [README.md](README.md)
- **Functional Specification**: [SPEC.md](SPEC.md)

### Module Documentation
- **Script Overview**: [README.md](README.md) - Complete script documentation

### Related Scripts

### Platform Navigation
- **Scripts Directory**: [../README.md](../README.md) - Scripts directory overview

## Agent Coordination

### Integration Points

When integrating with other scripts:

1. **Shared Utilities**: Use `_orchestrator_utils.py` for common CLI patterns
2. **Module Registry**: Coordinate with module discovery scripts
3. **Testing Integration**: Share testing templates with testing scripts
4. **Documentation Sync**: Keep documentation templates aligned

### Quality Gates

Before script changes are accepted:

1. **CLI Testing**: All command-line options work correctly
2. **Template Testing**: Generated modules work correctly
3. **Validation Testing**: Module validation works accurately
4. **Integration Testing**: Scripts work with core module system
5. **Template Testing**: All templates generate valid modules

## Version History

- **v0.1.0** (December 2025) - Initial module template automation scripts with scaffolding and template capabilities