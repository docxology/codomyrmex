# Codomyrmex Agents — src

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: December 2025

## Purpose

This is the source code coordination document for the core Codomyrmex platform implementation. It defines the modular source code architecture that provides all platform capabilities through independent, well-tested modules.

The src directory contains the Python package implementation with module system, API interfaces, and agent coordination capabilities.

## Source Architecture

### Package Structure

The source code follows a hierarchical module organization:

| Layer | Purpose | Location | Examples |
|-------|---------|----------|----------|
| **Package Root** | Package initialization and configuration | `src/` | `__init__.py`, package metadata |
| **Core Modules** | Primary platform capabilities | `src/codomyrmex/` | AI editing, analysis, execution |
| **Templates** | Code generation templates | `src/template/` | Module creation scaffolds |

### Module Categories

**Foundation Layer** - Base services used by all modules:
- `logging_monitoring/` - Centralized logging and telemetry
- `environment_setup/` - Environment validation and configuration
- `model_context_protocol/` - AI communication standards
- `terminal_interface/` - Rich terminal interactions

**Core Layer** - Primary development capabilities:
- `ai_code_editing/` - AI-powered code assistance
- `static_analysis/` - Code quality and security analysis
- `code_execution_sandbox/` - Safe code execution environments
- `data_visualization/` - Charts, plots, and visualizations
- `pattern_matching/` - Code pattern recognition
- `git_operations/` - Version control automation

**Service Layer** - Higher-level orchestration:
- `build_synthesis/` - Multi-language build automation
- `documentation/` - Documentation generation systems
- `api_documentation/` - API specification management
- `ci_cd_automation/` - Continuous integration pipelines
- `database_management/` - Database operations and migrations

## Active Components

### Package Infrastructure
- `README.md` – Source code documentation
- `__init__.py` – Package initialization and exports

### Core Module System
- `codomyrmex/` – Main package with 25+ specialized modules
- `template/` – Code generation and scaffolding templates

### Module Organization

Modules are self-contained with consistent structure:
- `module_name/` – Module directory
- `module_name/__init__.py` – Module initialization
- `module_name/core.py` – Primary module implementation
- `module_name/utils.py` – Module utilities and helpers
- `module_name/config.py` – Module configuration
- `module_name/exceptions.py` – Module-specific exceptions

## Operating Contracts

### Universal Source Protocols

All source code in this directory must:

1. **Follow Module Boundaries** - Each module maintains clear separation of concerns
2. **Adhere to Type Hints** - Type annotations for reliability
3. **Include Tests** - Unit and integration tests for all functionality
4. **Maintain API Stability** - Backward compatibility for public interfaces
5. **Follow Coding Standards** - Compliance with established coding rules

### Module-Specific Guidelines

#### Foundation Modules
- Provide stable, low-level services
- Minimize external dependencies
- Include error handling
- Support extensive configuration options

#### Core Modules
- Focus on specific development domains
- Provide clear, well-documented APIs
- Include performance optimizations
- Support both programmatic and CLI usage

#### Service Modules
- Coordinate multiple core modules
- Provide high-level abstractions
- Include workflow orchestration
- Support complex configuration scenarios

## Module Development

### Creating New Modules

Standard process for developing modules:

1. **Define Scope** - Clear module purpose and boundaries
2. **Design API** - Well-defined public interface
3. **Implement Core** - Functional implementation with error handling
4. **Add Configuration** - Flexible configuration system
5. **Write Tests** - Test coverage
6. **Document Usage** - Clear documentation and examples

### Module Standards

All modules must include:
- **API Specification** (`API_SPECIFICATION.md`) - Public interface documentation
- **Usage Examples** (`USAGE_EXAMPLES.md`) - Practical usage demonstrations
- **Security Considerations** (`SECURITY.md`) - Security implications and best practices
- **Change Log** (`CHANGELOG.md`) - Version history and updates

## Code Quality

### Quality Assurance

Source code quality maintained through:

**Automated Checks**
- Type checking with mypy
- Linting with ruff and pylint
- Code formatting with black
- Import sorting with isort

**Testing Standards**
- Unit test coverage ≥85%
- Integration test coverage ≥75%
- Performance regression testing
- Cross-platform compatibility validation

**Documentation Requirements**
- Docstrings
- API documentation generation
- Usage examples and tutorials
- Architecture documentation

## Package Distribution

### Installation Options

The package supports multiple installation methods:

```bash
# Development installation
pip install -e .

# Production installation
pip install codomyrmex

# With optional dependencies
pip install codomyrmex[all]
```

### Dependencies

Package dependencies organized by purpose:
- **Core** - Essential functionality
- **Optional** - Extended capabilities (AI, visualization, etc.)
- **Development** - Testing and development tools

## Navigation
- **Human Documentation**: [README.md](README.md)
- **Functional Specification**: [SPEC.md](SPEC.md)

### Signposting
- **Parent**: [Root](../AGENTS.md)
- **Self**: [Source Agents](AGENTS.md)
- **Children**:
    - [Codomyrmex Package](codomyrmex/AGENTS.md)
    - [Template Package](template/AGENTS.md)
- **Key Artifacts**:
    - [Functional Spec](SPEC.md)
    - [Human Readme](README.md)

### For Users
- **Installation**: [docs/getting-started/installation.md](../docs/getting-started/installation.md)
- **API Reference**: [../docs/reference/api.md](../docs/reference/api.md)
- **Module Guide**: [../docs/modules/overview.md](../docs/modules/overview.md)

### For Agents
- **Coding Standards**: [cursorrules/general.cursorrules](../cursorrules/general.cursorrules)
- **Module System**: [../docs/modules/overview.md](../docs/modules/overview.md)
- **API Documentation**: Generated from source docstrings

### For Contributors
- **Contributing**: [../docs/project/contributing.md](../docs/project/contributing.md)
- **Development Setup**: [docs/development/environment-setup.md](../docs/development/environment-setup.md)
- **Testing**: [testing/README.md](../testing/README.md)

## Agent Coordination

### Module Integration

When modules interact or depend on each other:

1. **Interface Stability** - Maintain stable public APIs
2. **Dependency Management** - Clear module dependency declarations
3. **Configuration Coordination** - Consistent configuration patterns
4. **Testing Integration** - Cross-module integration testing

### Quality Gates

Before source code changes are accepted:

1. **Tests Pass** - All existing tests continue to pass
2. **Coverage Maintained** - Test coverage requirements met
3. **Linting Clean** - No new linting errors introduced
4. **API Compatible** - No breaking changes to public interfaces
5. **Documentation Updated** - Code changes reflected in documentation

## Source Metrics

### Code Quality Metrics
- **Test Coverage** - Overall and per-module coverage percentages
- **Code Complexity** - Cyclomatic complexity measurements
- **Documentation Coverage** - Docstring and API documentation
- **Type Coverage** - Percentage of code with type annotations

### Maintenance Metrics
- **Technical Debt** - Code quality and maintainability scores
- **Dependency Freshness** - How current package dependencies are
- **Security Vulnerabilities** - Known security issues in dependencies
- **Performance Benchmarks** - Core functionality performance metrics

## Version History

- **v0.1.0** (December 2025) - Initial source code architecture with modular design

## Related Documentation

- **[Module System](../docs/modules/overview.md)** - Detailed module architecture and relationships
- **[API Reference](../docs/reference/api.md)** - API documentation
- **[Contributing Guide](../docs/project/contributing.md)** - Development standards and workflow
