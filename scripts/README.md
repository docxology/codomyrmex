# scripts

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: October 2025

## Overview

Maintenance and automation utilities for Codomyrmex project management.

## Core Capabilities

### Primary Functions

- **Modular Architecture**: Self-contained module with clear boundaries and responsibilities
- **Agent Integration**: Seamlessly integrates with Codomyrmex agent ecosystem
- **Comprehensive Testing**: Full test coverage with unit, integration, and performance tests
- **Documentation**: Complete documentation with examples and API references

## Architecture

```
scripts/
├── examples/                  # Example demonstrations
│   ├── basic/                # Basic single-module examples
│   └── integration/          # Multi-module integration examples
├── ollama_integration/        # Ollama LLM integration scripts
├── fabric_integration/        # Fabric AI framework integration
├── documentation/             # Documentation management utilities
├── maintenance/               # Code maintenance and quality tools
├── development/               # Development workflow enhancements
├── project_orchestration/     # Project orchestration scripts
│   └── examples/             # Orchestration workflow examples
├── git_operations/            # Git operations scripts
│   └── examples/             # Git visualization examples
├── docs/                     # Documentation and guides
└── [module_name]/            # Module-specific orchestrators (see below)
    └── orchestrate.py         # Thin CLI orchestrator for each module
```

## Key Components

### 📚 Documentation Management (`documentation/`)

- `check_docs_status.py` – Check documentation status across the entire repository.
- `documentation_status_summary.py` – Generate comprehensive documentation status summaries.
- `generate_missing_readmes.py` – Generate README.md files for directories with AGENTS.md.
- `verify_api_specs.py` – Verify API_SPECIFICATION.md files match actual code signatures.
- `check_completeness.py` – Check for placeholder content and generate implementation status tracker.

### 🔧 Code Quality & Maintenance (`maintenance/`)

- `add_logging.py` – Automated logging injection across modules.
- `fix_imports_simple.py` – Import statement cleanup and optimization.
- `fix_imports.py` – Advanced import management and dependency resolution.
- `fix_syntax_errors.py` – Syntax error detection and automated repair.
- `check_dependencies.py` – CI/CD script to validate module dependency hierarchy.

### 🚀 Development Tools (`development/`)

- `enhance_documentation.py` – Documentation enhancement and docstring generation.
- `generate_coverage_report.py` – Generate comprehensive test coverage reports and dashboards.
- `run_all_examples.sh` – Run all example scripts
- `test_examples.sh` – Test all example scripts
- `select_example.sh` – Interactive example selector
- `check_prerequisites.sh` – Check prerequisites for examples
- `example_usage.py` – Basic usage examples

### 📚 Examples (`examples/`)

- `basic/` – Basic single-module demonstrations
- `integration/` – Multi-module integration orchestrators

### 🐙 Ollama Integration (`ollama_integration/`)

- `basic_usage.py` – Simple Ollama model execution
- `integration_demo.py` – Comprehensive Ollama integration
- `model_management.py` – Ollama model management
- `orchestrate.py` – Main orchestrator

### 🧬 Fabric Integration (`fabric_integration/`)

- `setup_demo.sh` – Complete Fabric integration setup
- `orchestrate.py` – Main orchestrator

### 🎯 Project Orchestration (`project_orchestration/`)

- `demo.py` – Orchestrator demonstration
- `examples.py` – Orchestration examples
- `examples/` – Comprehensive workflow demos

## Module Orchestrators

Each Codomyrmex module has a corresponding orchestrator script in `scripts/[module_name]/orchestrate.py` that provides CLI access to module functionality. These are thin wrappers that call actual module functions while following established patterns from `cli.py` and proper exception handling.

### 🤖 AI & Intelligence

- **[ai_code_editing/](./ai_code_editing/)** – AI-powered code generation, refactoring, and analysis
  - Commands: `generate`, `refactor`, `analyze`, `validate-api-keys`, `list-providers`, `list-languages`, `list-models`

- **[language_models/](./language_models/)** – Local LLM integration and Ollama management
  - Commands: `check-availability`, `list-models`, `config`

- **[model_context_protocol/](./model_context_protocol/)** – LLM interaction framework
  - Commands: `info`, `list-tools`

- **[ollama_integration/](./ollama_integration/)** – Comprehensive Ollama integration
  - Commands: `info`

- **[pattern_matching/](./pattern_matching/)** – Advanced pattern recognition and code analysis
  - Commands: `analyze`, `full-analysis`

### 📊 Analysis & Visualization

- **[data_visualization/](./data_visualization/)** – Plotting and visualization tools
  - Commands: `line-plot`, `scatter-plot`, `bar-chart`, `histogram`, `pie-chart`, `heatmap`, `git-visualize`

- **[static_analysis/](./static_analysis/)** – Code quality and security analysis
  - Commands: `analyze-file`, `analyze-project`, `list-tools`

- **[code_review/](./code_review/)** – Automated code review and quality analysis
  - Commands: `analyze-file`, `analyze-project`, `generate-report`

- **[security_audit/](./security_audit/)** – Security analysis and compliance checking
  - Commands: `scan-vulnerabilities`, `audit-code`, `check-compliance`, `generate-report`

### 🛠️ Development Infrastructure

- **[environment_setup/](./environment_setup/)** – Development environment management
  - Commands: `check-dependencies`, `setup-env-vars`, `check-uv`

- **[code_execution_sandbox/](./code_execution_sandbox/)** – Secure code execution
  - Commands: `execute`

- **[build_synthesis/](./build_synthesis/)** – Build automation and code synthesis
  - Commands: `check-environment`, `build`, `trigger-build`, `list-build-types`, `list-environments`

- **[git_operations/](./git_operations/)** – Git workflow automation
  - Commands: `status`, `branch`, `add`, `commit`, `push`, `pull`, `clone`, `init`, `history`, `check`

### 📚 Documentation & Management

- **[documentation_module/](./documentation_module/)** – Documentation website generation (Docusaurus)
  - Commands: `check-environment`, `build`, `dev-server`, `aggregate`, `assess`

- **[api_documentation/](./api_documentation/)** – API documentation generation
  - Commands: `generate-docs`, `extract-specs`, `generate-openapi`, `validate-openapi`

- **[project_orchestration/](./project_orchestration/)** – Workflow and project management
  - Commands: `list-workflows`, `run-workflow`, `list-projects`, `status`, `health`

### 🔧 System & Operations

- **[logging_monitoring/](./logging_monitoring/)** – Structured logging system
  - Commands: `test-logging`, `info`

- **[performance/](./performance/)** – Performance optimization utilities
  - Commands: `monitor-stats`, `cache-info`

- **[system_discovery/](./system_discovery/)** – System introspection and capability mapping
  - Commands: `status`, `scan`, `discover`

- **[terminal_interface/](./terminal_interface/)** – Interactive CLI and terminal utilities
  - Commands: `shell`, `format`

### 🏗️ Infrastructure & Deployment

- **[ci_cd_automation/](./ci_cd_automation/)** – CI/CD pipeline management
  - Commands: `create-pipeline`, `run-pipeline`, `monitor-health`, `generate-reports`

- **[containerization/](./containerization/)** – Container management and orchestration
  - Commands: `build`, `scan`

- **[config_management/](./config_management/)** – Configuration management
  - Commands: `load-config`, `validate-config`

- **[database_management/](./database_management/)** – Database operations
  - Commands: `backup`, `migrate`

### 🎨 Advanced Features

- **[modeling_3d/](./modeling_3d/)** – 3D modeling and rendering
  - Commands: `info`

- **[physical_management/](./physical_management/)** – Physical object management and simulation
  - Commands: `info`

- **[module_template/](./module_template/)** – Module scaffolding template
  - Commands: `info`

## Operating Contracts

- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.

## Integration Points

### Related Modules

No related modules specified

## Usage Examples

### Documentation Management

```bash
# Check documentation status
python scripts/documentation/check_docs_status.py

# Generate documentation summary
python scripts/documentation/documentation_status_summary.py

# Generate missing README files
python scripts/documentation/generate_missing_readmes.py
```

### Code Maintenance

```bash
# Fix import statements
python scripts/maintenance/fix_imports.py

# Add logging to modules
python scripts/maintenance/add_logging.py

# Check module dependencies
python scripts/maintenance/check_dependencies.py
```

### Development Tools

```bash
# Enhance documentation
python scripts/development/enhance_documentation.py

# Generate coverage report
python scripts/development/generate_coverage_report.py

# Run examples
./scripts/development/run_all_examples.sh

# Test examples
./scripts/development/test_examples.sh

# Check prerequisites
./scripts/development/check_prerequisites.sh
```

### Examples

```bash
# Basic examples
./scripts/examples/basic/data-visualization-demo.sh
./scripts/examples/basic/static-analysis-demo.sh

# Integration examples
./scripts/examples/integration/environment-health-monitor.sh
./scripts/examples/integration/code-quality-pipeline.sh
```

### Integration Scripts

```bash
# Ollama integration
python scripts/ollama_integration/basic_usage.py
python scripts/ollama_integration/integration_demo.py

# Fabric integration
./scripts/fabric_integration/setup_demo.sh
```

### Module Orchestrators

```bash
# AI code generation
python scripts/ai_code_editing/orchestrate.py generate "create a function" --language python

# Data visualization
python scripts/data_visualization/orchestrate.py line-plot --output plot.png --title "My Plot"

# Code analysis
python scripts/static_analysis/orchestrate.py analyze-project . --output analysis.json

# Git operations
python scripts/git_operations/orchestrate.py status

# Build pipeline
python scripts/build_synthesis/orchestrate.py build --config build.json

# Project orchestration
python scripts/project_orchestration/orchestrate.py list-workflows
```

See individual module orchestrator README files for complete usage examples.

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

## Related Documentation

- **[AGENTS.md](./AGENTS.md)**: Detailed agent configuration and purpose
- **[Main Package README](../src/codomyrmex/README.md)**: Complete module documentation
- **[CLI Reference](../docs/reference/cli.md)**: Main CLI documentation
- **[Module Documentation](../src/codomyrmex/*/README.md)**: Individual module documentation

Each module orchestrator has its own README.md with usage examples and integration details.
