# Codomyrmex Agents — src/codomyrmex

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: December 2025

## Purpose

Core package containing the Codomyrmex platform implementation. This directory houses all functional modules that provide the platform's capabilities, organized into a layered architecture for maintainability and extensibility.

The codomyrmex package serves as the central hub for all platform functionality, with modules that can be composed together to create complex workflows and applications.

## Package Architecture

### Layered Design

Modules are organized into functional layers:

**Foundation Layer** - Base services used throughout the platform:
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

**Specialized Layer** - Domain-specific capabilities:
- `modeling_3d/` - 3D modeling and visualization
- `physical_management/` - Hardware resource management
- `system_discovery/` - Module discovery and health monitoring

## Active Components

### Package Infrastructure
- `__init__.py` – Package initialization and public API exports
- `README.md` – Package overview and module documentation
- `cli.py` – Command-line interface for the platform
- `exceptions.py` – Platform-wide exception definitions

### Module Directories
- `ai_code_editing/` – AI-assisted code generation and editing
- `api_documentation/` – API documentation generation
- `build_synthesis/` – Build orchestration and automation
- `ci_cd_automation/` – CI/CD pipeline management
- `code_execution_sandbox/` – Safe code execution environments
- `code_review/` – Automated code review and analysis
- `config_management/` – Configuration management and validation
- `containerization/` – Container lifecycle management
- `data_visualization/` – Data plotting and visualization
- `database_management/` – Database operations and maintenance
- `documentation/` – Documentation generation system
- `environment_setup/` – Environment validation and setup
- `git_operations/` – Git workflow automation
- `language_models/` – Language model management
- `logging_monitoring/` – Centralized logging system
- `model_context_protocol/` – MCP tool specifications
- `modeling_3d/` – 3D modeling and rendering
- `module_template/` – Module creation templates
- `ollama_integration/` – Local LLM integration
- `pattern_matching/` – Code pattern analysis
- `performance/` – Performance monitoring and optimization
- `physical_management/` – Hardware resource management
- `project_orchestration/` – Workflow orchestration
- `security_audit/` – Security scanning and compliance
- `static_analysis/` – Code quality analysis
- `system_discovery/` – System exploration and discovery
- `template/` – Code generation templates
- `terminal_interface/` – Rich terminal UI components
- `tests/` – Cross-module integration tests
- `tools/` – Utility tools and helpers

## Operating Contracts

### Universal Package Protocols

All code in this package must:

1. **Follow Module Boundaries** - Each module maintains clear separation of concerns
2. **Adhere to Type Hints** - Comprehensive type annotations for reliability
3. **Include Comprehensive Tests** - Unit and integration tests for all functionality
4. **Maintain API Stability** - Backward compatibility for public interfaces
5. **Follow Coding Standards** - Compliance with established platform rules

### Module Development Standards

#### Module Structure
Each module must include:
- `__init__.py` - Module initialization and exports
- Core implementation files with clear naming
- Comprehensive documentation (README.md, API_SPECIFICATION.md, etc.)
- Test suites with good coverage
- Requirements.txt for dependencies

#### Quality Requirements
- PEP 8 compliance and type hints
- Docstrings for all public functions
- Error handling with informative messages
- Logging integration for monitoring
- Security considerations documented

## Navigation Links

### Package Documentation
- **Package Overview**: [README.md](README.md) - Complete package documentation
- **Module System**: [docs/modules/overview.md](../../../docs/modules/overview.md) - Module architecture

### Development Resources
- **Contributing**: [docs/project/contributing.md](../../../docs/project/contributing.md) - Development guidelines
- **Coding Standards**: [cursorrules/general.cursorrules](../../../cursorrules/general.cursorrules) - Platform standards

### Related Systems
- **Scripts**: [scripts/](../../scripts/) - Automation and maintenance utilities
- **Testing**: [testing/](../../testing/) - Test suites and validation
- **Configuration**: [config/](../../config/) - Configuration management
