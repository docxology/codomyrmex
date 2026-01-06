# Codomyrmex Agents — projects

## Signposting
- **Parent**: [Parent](../AGENTS.md)
- **Self**: [Agents](AGENTS.md)
- **Children**:
    - [test_project](test_project/AGENTS.md)
- **Key Artifacts**:
    - [Functional Spec](SPEC.md)
    - [Human Readme](README.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: December 2025

## Purpose

This is the projects coordination document for all project workspaces, templates, and example implementations in the Codomyrmex repository. It defines the project scaffolding system that enables rapid development of new projects using Codomyrmex modules.

The projects directory serves as a workspace for project templates, example implementations, and development sandboxes that demonstrate Codomyrmex capabilities.

## Project Types

### Template Categories

Projects are organized by purpose and complexity:

| Type | Purpose | Examples |
|------|---------|----------|
| **Starter Projects** | Basic project scaffolding | Minimal viable projects |
| **Example Projects** | Feature demonstrations | Module usage examples |
| **Reference Projects** | Best practice implementations | Production-ready examples |
| **Test Projects** | Validation and testing | Development sandboxes |

### Project Structure

All projects follow consistent structure:

```
project_name/
├── src/                 # Source code
├── tests/              # Test suites
├── docs/               # Project documentation
├── config/             # Configuration files
├── scripts/            # Automation scripts
├── AGENTS.md           # Agent coordination
└── README.md           # Project documentation
```

## Project Templates

### Template Components

Projects provide reusable templates for:

**Project Structure**
- Standardized directory layouts
- Configuration file templates
- Documentation templates
- Build and deployment scripts

**Module Integration**
- Module import patterns
- Configuration examples
- Usage demonstrations
- Integration test templates

**Development Workflow**
- Git workflow setup
- CI/CD pipeline templates
- Code quality tooling
- Testing frameworks

## Active Components

### Core Project Infrastructure
- `README.md` – Projects directory documentation

### Example Projects
- `test_project/` – Example project demonstrating Codomyrmex usage

### Project Assets

**test_project/ Structure:**
- `src/` – Example source code and module usage
- `config/` – Configuration examples and templates
- `data/` – Sample data for demonstrations
- `reports/` – Generated reports and outputs
- `docs/` – Project documentation and guides

## Operating Contracts

### Universal Project Protocols

All projects in this directory must:

1. **Demonstrate Best Practices** - Projects show recommended usage patterns
2. **Remain Current** - Projects updated to reflect latest Codomyrmex features
3. **Include Tests** - Projects demonstrate testing approaches
4. **Provide Clear Documentation** - Projects document their purpose and usage
5. **Support Multiple Environments** - Projects work across different deployment scenarios

### Project-Specific Guidelines

#### Template Projects
- Provide clear setup instructions
- Include realistic example data
- Demonstrate common use cases
- Support easy customization

#### Example Projects
- Focus on specific feature demonstrations
- Include step-by-step tutorials
- Provide working code examples
- Document integration patterns

#### Reference Projects
- Follow production best practices
- Include error handling
- Demonstrate scaling and performance
- Provide deployment examples

## Project Development

### Creating New Projects

Process for developing new project templates:

1. **Define Purpose** - Clear project goals and target audience
2. **Design Structure** - Follow established project patterns
3. **Implement Features** - Use current Codomyrmex modules and practices
4. **Add Documentation** - Setup and usage guides
5. **Include Tests** - Full test coverage and validation
6. **Validate Functionality** - Ensure project works end-to-end

### Project Maintenance

Regular project maintenance includes:
- Updating to latest module versions
- Refreshing dependencies and configurations
- Adding new feature demonstrations
- Updating documentation and examples
- Performance optimization and improvements

## Project Usage

### Getting Started with Projects

```bash
# Clone project template
cp -r projects/test_project my_new_project
cd my_new_project

# Customize for your needs
# Edit configuration files
# Add your specific requirements
# Update documentation
```

### Project Configuration

Projects support configuration through:
- Environment-specific config files
- Command-line parameters
- Configuration validation
- Secret management integration

## Navigation
- **Human Documentation**: [README.md](README.md)
- **Functional Specification**: [SPEC.md](SPEC.md)

### For Users
- **Quick Start**: [test_project/](test_project) - Working example
- **Templates**: Browse available project templates
- **Examples**: Feature-specific usage examples

### For Agents
- **Project Standards**: [cursorrules/general.cursorrules](../cursorrules/general.cursorrules)
- **Module System**: [docs/modules/overview.md](../docs/modules/overview.md)
- **Configuration**: [config/templates/](../config/templates/)

### For Contributors
- **Contributing**: [docs/project/contributing.md](../docs/project/contributing.md)
- **Project Creation**: Guidelines for creating new project templates
- **Template Standards**: [docs/project_orchestration/project-template-schema.md](../docs/project_orchestration/project-template-schema.md)

## Agent Coordination

### Project Synchronization

When projects need updates across the system:

1. **Template Updates** - Modify base templates to reflect changes
2. **Example Updates** - Update examples to demonstrate new features
3. **Documentation Sync** - Ensure project documentation stays current
4. **Validation Updates** - Update project validation and testing

### Quality Gates

Before project changes are accepted:

1. **Functionality Verified** - Projects work correctly end-to-end
2. **Documentation Complete** - All features and usage documented
3. **Tests Pass** - Test coverage maintained
4. **Standards Compliance** - Follows all coding and project standards
5. **Integration Validated** - Works with current module versions

## Project Metrics

### Quality Metrics
- **Template Utilization** - How often templates are used for new projects
- **Example Freshness** - How current examples remain with platform updates
- **Documentation Coverage** - Percentage of features documented in projects
- **Test Coverage** - Test coverage across all example projects

### Usage Metrics
- **Project Creation Rate** - Frequency of new projects created from templates
- **Feature Adoption** - Which features are most commonly used in projects
- **Customization Patterns** - Common modifications made to templates

## Version History

- **v0.1.0** (December 2025) - Initial project template system with example project

## Related Documentation

- **[Project Orchestration](../docs/project_orchestration/project-lifecycle-guide.md)** - Project development lifecycle
- **[Module System](../docs/modules/overview.md)** - Available modules for projects
- **[Contributing Guide](../docs/project/contributing.md)** - Project contribution guidelines