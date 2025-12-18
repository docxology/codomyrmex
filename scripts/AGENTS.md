# Codomyrmex Agents — scripts

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: December 2025

## Purpose

This is the scripts coordination document for all automation utilities in the Codomyrmex repository. It defines the maintenance and automation utilities that support project management, module orchestration, and development workflows.

The scripts directory contains executable utilities that automate common development tasks, module management, and system operations across the entire Codomyrmex platform.

## Directory Structure

### Core Script Categories

The scripts are organized by functionality:

| Category | Purpose | Key Scripts |
|----------|---------|-------------|
| **development/** | Development workflow automation | Setup, testing, linting, formatting |
| **documentation/** | Documentation generation and maintenance | API docs, website generation, audits |
| **maintenance/** | System maintenance and cleanup | Database management, file organization |
| **examples/** | Demonstration and example scripts | Usage examples, tutorials |
| **[module-specific]/** | Module-specific automation | Per-module utilities and orchestrators |

### Module-Specific Scripts

Each module has dedicated automation scripts:
- `ai_code_editing/` - AI-assisted code generation and editing workflows
- `api_documentation/` - API specification generation and validation
- `build_synthesis/` - Multi-language build orchestration
- `ci_cd_automation/` - Continuous integration pipeline management
- `code_execution_sandbox/` - Safe code execution environments
- `code_review/` - Automated code review and quality analysis
- `config_management/` - Configuration validation and deployment
- `containerization/` - Docker and container lifecycle management
- `data_visualization/` - Chart generation and data plotting
- `database_management/` - Database operations and migrations
- `git_operations/` - Version control automation
- `language_models/` - LLM management and benchmarking
- `logging_monitoring/` - Centralized logging configuration
- `model_context_protocol/` - MCP tool specification management
- `modeling_3d/` - 3D visualization and modeling
- `ollama_integration/` - Local LLM integration
- `pattern_matching/` - Code pattern analysis
- `performance/` - Performance monitoring and profiling
- `physical_management/` - Hardware resource management
- `project_orchestration/` - Workflow orchestration
- `security_audit/` - Security scanning and compliance
- `static_analysis/` - Code quality analysis
- `system_discovery/` - Module discovery and health monitoring
- `terminal_interface/` - Rich terminal UI components

## Active Components

### Core Files
- `README.md` – Scripts directory documentation
- `_orchestrator_utils.py` – Shared utilities for script orchestration

### Module Script Directories
- `ai_code_editing/` – AI-powered code assistance automation
- `api_documentation/` – API documentation generation tools
- `build_synthesis/` – Build pipeline orchestration
- `ci_cd_automation/` – CI/CD workflow management
- `code_execution_sandbox/` – Safe execution environment setup
- `code_review/` – Code review automation
- `config_management/` – Configuration management utilities
- `containerization/` – Container lifecycle management
- `data_visualization/` – Data visualization automation
- `database_management/` – Database operations and maintenance
- `development/` – Development workflow scripts
- `docs/` – Documentation maintenance utilities
- `documentation/` – Documentation generation system
- `documentation_module/` – Module documentation tools
- `environment_setup/` – Environment validation and setup
- `examples/` – Example scripts and demonstrations
- `fabric_integration/` – Fabric AI framework integration
- `git_operations/` – Git workflow automation
- `language_models/` – Language model management
- `logging_monitoring/` – Logging system configuration
- `maintenance/` – System maintenance utilities
- `model_context_protocol/` – MCP tool management
- `modeling_3d/` – 3D modeling utilities
- `module_template/` – Module creation templates
- `ollama_integration/` – Local LLM integration tools
- `pattern_matching/` – Pattern analysis automation
- `performance/` – Performance monitoring tools
- `physical_management/` – Hardware management scripts
- `project_orchestration/` – Project workflow orchestration
- `security_audit/` – Security scanning utilities
- `static_analysis/` – Code analysis tools
- `system_discovery/` – System exploration utilities
- `terminal_interface/` – Terminal interface components

## Operating Contracts

### Universal Script Protocols

All scripts in this directory must:

1. **Idempotent Operations**: Scripts should be safe to run multiple times
2. **Error Handling**: Comprehensive error handling with informative messages
3. **Logging Integration**: Use centralized logging system for all operations
4. **Configuration Management**: Respect configuration files and environment variables
5. **Documentation**: Include usage documentation and help text

### Script-Specific Guidelines

#### Development Scripts
- Follow TDD practices for script development
- Include comprehensive testing
- Handle edge cases gracefully
- Provide clear success/failure feedback

#### Maintenance Scripts
- Backup critical data before modifications
- Provide dry-run options where applicable
- Log all significant operations
- Include rollback capabilities

#### Module Scripts
- Respect module boundaries and dependencies
- Coordinate with other module scripts through shared utilities
- Update module documentation when making changes

## Navigation

### For Users
- **Quick Start**: [development/setup.sh](../../scripts/development/setup.sh) - Environment setup
- **Examples**: [examples/](../../scripts/examples/) - Usage examples and demonstrations
- **Maintenance**: [maintenance/](../../scripts/maintenance/) - System maintenance utilities

### For Agents
- **Coding Standards**: [cursorrules/general.cursorrules](../../../cursorrules/general.cursorrules)
- **Script Development**: [development/README.md](../../scripts/development/README.md)
- **Module System**: [docs/modules/overview.md](../../../docs/modules/overview.md)

### For Contributors
- **Script Templates**: [module_template/](../../scripts/module_template/) - Script creation templates
- **Testing**: [testing/unit/](../../testing/unit/) - Script testing guidelines
- **Contributing**: [docs/project/contributing.md](../../../docs/project/contributing.md)

## Agent Coordination

### Cross-Script Operations

When scripts interact or depend on each other:

1. **Shared Utilities**: Use `_orchestrator_utils.py` for common functionality
2. **Consistent Logging**: Maintain consistent log levels and structured data
3. **Dependency Management**: Document script dependencies and execution order
4. **State Management**: Coordinate through shared state files when necessary

### Quality Gates

Before deploying script changes:

1. **Testing**: All scripts pass their test suites
2. **Documentation**: Script usage is documented and current
3. **Linting**: Scripts pass linting and style checks
4. **Integration**: Scripts work correctly with the broader system

## Version History

- **v0.1.0** (December 2025) - Initial script system and module automation framework

## Related Documentation

- **[Script Development Guide](development/README.md)** - Guidelines for creating new scripts
- **[Module Orchestration](docs/modules/overview.md)** - Module system documentation
- **[Testing Strategy](docs/development/testing-strategy.md)** - Testing approach for scripts
