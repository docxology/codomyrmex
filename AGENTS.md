# Codomyrmex Agents — Repository Root

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: December 2025

## Purpose

This is the root coordination document for all AI agents operating within the Codomyrmex repository. It defines the top-level structure, surfaces, and operating contracts that govern agent interactions across the entire project.

Codomyrmex is a modular coding workspace enabling AI-enhanced development workflows. This document serves as the central navigation hub for agents working with any part of the system.

## Repository Structure

### Primary Surfaces

The repository is organized into distinct surfaces, each with specific responsibilities:

| Surface | Purpose | Documentation |
|---------|---------|---------------|
| **src/** | Core source modules implementing functionality | [src/README.md](src/README.md) |
| **scripts/** | Maintenance and automation utilities | [scripts/README.md](scripts/README.md) |
| **docs/** | Project documentation (about Codomyrmex) | [docs/README.md](docs/README.md) |
| **testing/** | Test suites (unit and integration) | [testing/README.md](testing/README.md) |
| **config/** | Configuration templates and examples | [config/README.md](config/README.md) |
| **cursorrules/** | Coding standards and automation rules | [cursorrules/README.md](cursorrules/README.md) |
| **projects/** | Project workspace and templates | [projects/README.md](projects/README.md) |
| **examples/** | Example scripts and demonstrations | [examples/README.md](examples/README.md) |
| **scripts/examples/** | Executable examples and demos | [scripts/examples/README.md](scripts/examples/README.md) |

### Repository Root Files

- `README.md` - Primary entry point for users and contributors
- `AGENTS.md` - This file: agent coordination and navigation
- `LICENSE` - MIT License
- `SECURITY.md` - Security policies and vulnerability reporting
- `pyproject.toml` - Python package configuration
- `pytest.ini` - Test configuration
- `Makefile` - Build and automation tasks
- `start_here.sh` - Interactive entry point for exploration
- `package.json` - Node.js package configuration
- `uv.lock` - Python dependency lock file
- `general.cursorrules` - General coding standards
- `resources.json` - Resource configuration
- `demo_plot.png` - Demonstration visualization
- `test.db` - Test database file
- `workflow.db` - Workflow database file

## Operating Contracts

### Universal Agent Protocols

All agents operating within this repository must:

1. **Respect Modularity**: Each module is self-contained. Changes within one module should minimize impact on others.

2. **Maintain Documentation Alignment**: Code, documentation, and workflows must remain synchronized. When updating code, update corresponding documentation.

3. **Follow Cursorrules**: Adhere to coding standards defined in `cursorrules/general.cursorrules` and module-specific rules.

4. **Use Structured Logging**: All operations must use the centralized logging system (`src/codomyrmex/logging_monitoring/`).

5. **Preserve Model Context Protocol Interfaces**: MCP tool specifications must remain available and functional for sibling agents.

6. **Record Telemetry**: Outcomes and metrics should be recorded in shared telemetry systems.

7. **Update TODO Queues**: Maintain TODO items for pending work and cross-agent coordination.

### Surface-Specific Guidelines

#### src/ - Source Code
- Follow Python best practices (PEP 8)
- Maintain comprehensive test coverage (≥80%)
- Update `API_SPECIFICATION.md` when changing interfaces
- Document MCP tools in `MCP_TOOL_SPECIFICATION.md`
- Version changes in `CHANGELOG.md`

#### scripts/ - Automation
- Scripts should be idempotent where possible
- Include usage documentation in script headers
- Log all significant operations
- Handle errors gracefully with informative messages

#### docs/ - Documentation
- Documentation is about Codomyrmex (not tools Codomyrmex provides)
- Use clear, understated language ("show not tell")
- Maintain navigation links between related documents
- Keep examples current with codebase

#### testing/ - Tests
- Follow test-driven development (TDD) practices
- Use real data analysis (no mock methods)
- Organize by test type (unit, integration)
- Include performance benchmarks where applicable

## Module Discovery

### Core Functional Modules

Located in `src/codomyrmex/`, these modules provide the primary capabilities:

**Foundation Layer**:
- `logging_monitoring/` - Centralized logging system
- `environment_setup/` - Environment validation and setup
- `model_context_protocol/` - AI communication standards
- `terminal_interface/` - Rich terminal interactions

**Core Layer**:
- `ai_code_editing/` - AI-powered code assistance
- `static_analysis/` - Code quality analysis
- `code_execution_sandbox/` - Safe code execution
- `data_visualization/` - Charts and plots
- `pattern_matching/` - Code pattern analysis
- `git_operations/` - Version control automation
- `code_review/` - Automated code review
- `security_audit/` - Security scanning
- `ollama_integration/` - Local LLM integration
- `language_models/` - LLM infrastructure
- `performance/` - Performance monitoring

**Service Layer**:
- `build_synthesis/` - Build automation
- `documentation/` - Documentation generation tools
- `api_documentation/` - API documentation generation
- `ci_cd_automation/` - CI/CD pipeline management
- `containerization/` - Container management
- `database_management/` - Database operations
- `project_orchestration/` - Workflow orchestration
- `config_management/` - Configuration management

**Specialized Layer**:
- `modeling_3d/` - 3D modeling and visualization
- `physical_management/` - Physical system simulation
- `system_discovery/` - System exploration and module discovery

**Development Layer**:
- `module_template/` - Module creation templates and scaffolding
- `template/` - Code generation templates

See [docs/modules/overview.md](docs/modules/overview.md) for complete module documentation.

## Navigation

### For Users
- **Start Here**: [README.md](README.md) - Project overview and quick start
- **Getting Started**: [docs/getting-started/quickstart.md](docs/getting-started/quickstart.md)
- **Architecture**: [docs/project/architecture.md](docs/project/architecture.md)
- **Contributing**: [docs/project/contributing.md](docs/project/contributing.md)

### For Agents
- **Coding Standards**: [cursorrules/general.cursorrules](cursorrules/general.cursorrules)
- **Module System**: [docs/modules/overview.md](docs/modules/overview.md)
- **Module Relationships**: [docs/modules/relationships.md](docs/modules/relationships.md)
- **API Reference**: [docs/reference/api.md](docs/reference/api.md)

### For Contributors
- **Development Setup**: [docs/development/environment-setup.md](docs/development/environment-setup.md)
- **Testing Strategy**: [docs/development/testing-strategy.md](docs/development/testing-strategy.md)
- **Documentation Guide**: [docs/development/documentation.md](docs/development/documentation.md)

## Active Components
- `@output/` – Generated output and reports directory
- `AGENTS.md` – This file: agent coordination and navigation
- `LICENSE` – MIT License
- `Makefile` – Build and automation tasks
- `README.md` – Primary entry point for users and contributors
- `SECURITY.md` – Security policies and vulnerability reporting
- `.editorconfig` – Editor configuration standards
- `.pre-commit-config.yaml` – Pre-commit hook configuration
- `config/` – Configuration templates and examples
- `coverage.json` – Code coverage report data
- `cursorrules/` – Coding standards and automation rules
- `demo_plot.png` – Demonstration visualization
- `docs/` – Project documentation (about Codomyrmex)
- `examples/` – Example scripts and demonstrations
- `general.cursorrules` – General coding standards
- `output/` – Additional output and validation results
- `package.json` – Node.js package configuration
- `projects/` – Project workspace and templates
- `pyproject.toml` – Python package configuration
- `pytest.ini` – Test configuration
- `resources.json` – Resource configuration
- `scripts/` – Maintenance and automation utilities
- `setup.py` – Python package setup script
- `src/` – Core source modules implementing functionality
- `start_here.sh` – Interactive entry point for exploration
- `test.db` – Test database file
- `testing/` – Test suites (unit and integration)
- `uv.lock` – Python dependency lock file
- `workflow.db` – Workflow database file

## Navigation Links
- **Main Documentation**: [README.md](README.md) - Main project README
- **Documentation Hub**: [docs/README.md](docs/README.md) - Documentation structure
- **Source Code**: [src/README.md](src/README.md) - Source code structure
- **Scripts**: [scripts/README.md](scripts/README.md) - Scripts directory
- **Testing**: [testing/README.md](testing/README.md) - Testing suite
- **Configuration**: [config/README.md](config/README.md) - Configuration templates
- **Cursor Rules**: [cursorrules/README.md](cursorrules/README.md) - Coding standards
- **Projects**: [projects/README.md](projects/README.md) - Projects workspace
- **Examples**: [examples/README.md](examples/README.md) - Example implementations
- **Scripts Examples**: [scripts/examples/README.md](scripts/examples/README.md) - Executable examples and demos
- **Source Agents**: [src/AGENTS.md](src/AGENTS.md) - Source code agent coordination
- **Docs Agents**: [docs/AGENTS.md](docs/AGENTS.md) - Documentation agent coordination
- **Scripts Agents**: [scripts/AGENTS.md](scripts/AGENTS.md) - Scripts agent coordination
- **Testing Agents**: [testing/AGENTS.md](testing/AGENTS.md) - Testing agent coordination
- **Config Agents**: [config/AGENTS.md](config/AGENTS.md) - Configuration agents
- **Rules Agents**: [cursorrules/AGENTS.md](cursorrules/AGENTS.md) - Cursor rules agents
- **Projects Agents**: [projects/AGENTS.md](projects/AGENTS.md) - Projects agent coordination

## Agent Coordination

### Cross-Module Operations

When an operation spans multiple modules:

1. **Check Dependencies**: Review `docs/modules/relationships.md` for dependency graph
2. **Coordinate Logging**: Use consistent log levels and structured data
3. **Share Context**: Use MCP tools to pass context between agents
4. **Update Documentation**: Ensure all affected modules' docs are updated

### Conflict Resolution

If conflicting guidance is found:

1. **Hierarchy**: Specific overrides general (module rules > general rules)
2. **Rationale**: Conflicts should state explicit rationale
3. **Escalation**: Document unresolved conflicts in TODO items

### Quality Gates

Before completing significant changes:

1. **Tests Pass**: All relevant tests must pass
2. **Linting Clean**: No new linting errors
3. **Documentation Updated**: Changes reflected in docs
4. **AGENTS.md Current**: Module AGENTS.md reflects changes
5. **Links Valid**: All documentation links functional

## Version History

- **v0.1.0** (December 2025) - Initial repository structure and agent coordination framework

## Related Documentation

- **[Module Overview](docs/modules/overview.md)** - Complete module system documentation
- **[Architecture](docs/project/architecture.md)** - System architecture and design principles
- **[Cursorrules](cursorrules/README.md)** - Detailed coding standards and automation rules
- **[Contributing](docs/project/contributing.md)** - Contributing guidelines and workflow
