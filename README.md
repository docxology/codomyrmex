# Codomyrmex

**Version**: 0.1.0 | **License**: MIT | **Python**: ≥3.10

A modular, extensible coding workspace designed for AI-enhanced development workflows. Codomyrmex integrates tools for building, documenting, analyzing, executing, and visualizing code across multiple languages.

## Overview

Codomyrmex provides a comprehensive suite of development tools organized as independent, composable modules. Each module offers specific functionality while maintaining clear interfaces and minimal coupling, enabling flexible composition and easy extensibility.

**Key Design Principles**:
- **Modularity First**: Self-contained modules with clear boundaries
- **AI Integration**: Built-in support for Large Language Models via Model Context Protocol (MCP)
- **Polyglot Support**: Language-agnostic interfaces with pluggable implementations
- **Professional Quality**: Comprehensive testing, documentation, and security practices

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/codomyrmex/codomyrmex.git
cd codomyrmex

# Install with uv (recommended)
uv sync

# Or with pip
pip install -e .
```

### Basic Usage

```bash
# Launch interactive shell
./start_here.sh

# Or use the CLI directly
codomyrmex --help

# Discover available modules
python -c "from codomyrmex.system_discovery import SystemDiscovery; SystemDiscovery().discover_modules()"
```

## Core Modules

### Foundation Layer
Essential infrastructure used by all other modules:

| Module | Purpose | Key Features |
|--------|---------|-------------|
| **logging_monitoring** | Centralized logging system | Structured logging, multiple formats, aggregation |
| **environment_setup** | Environment validation | Dependency checking, API key management, setup automation |
| **model_context_protocol** | AI communication standard | Standardized LLM interfaces, tool specifications |
| **terminal_interface** | Rich terminal interactions | Colored output, progress bars, interactive prompts |

### Core Functional Modules
Primary capabilities for development workflows:

| Module | Purpose | Key Features |
|--------|---------|-------------|
| **ai_code_editing** | AI-powered code assistance | Code generation, refactoring, multi-LLM support |
| **static_analysis** | Code quality analysis | Linting, security scanning, complexity metrics |
| **code_execution_sandbox** | Safe code execution | Multi-language support, resource limits, isolation |
| **data_visualization** | Charts and plots | Static/interactive plots, multiple formats |
| **pattern_matching** | Code pattern analysis | Pattern recognition, dependency analysis |
| **git_operations** | Version control automation | Git workflows, branch management, commit automation |
| **code_review** | Automated code review | AI-powered review, quality analysis, suggestions |
| **ollama_integration** | Local LLM integration | Local model management, execution, benchmarking |
| **security_audit** | Security scanning | Vulnerability detection, compliance checking |
| **language_models** | LLM infrastructure | Model management, API integration, benchmarking |
| **performance** | Performance monitoring | Profiling, optimization, benchmarking |

### Service Modules
Higher-level services that orchestrate core modules:

| Module | Purpose | Key Features |
|--------|---------|-------------|
| **build_synthesis** | Build automation | Multi-language builds, artifact generation, pipelines |
| **documentation** | Documentation generation | Website generation, API docs, tutorial creation |
| **api_documentation** | API documentation | OpenAPI/Swagger specs, structured documentation |
| **ci_cd_automation** | CI/CD pipeline management | Pipeline orchestration, deployment automation |
| **containerization** | Container management | Docker lifecycle, Kubernetes orchestration |
| **database_management** | Database operations | Schema management, migrations, backups |
| **config_management** | Configuration management | Environment setup, secret management, validation |
| **project_orchestration** | Workflow orchestration | Workflow management, task coordination |

### Specialized Modules
Advanced capabilities for specific domains:

| Module | Purpose | Key Features |
|--------|---------|-------------|
| **modeling_3d** | 3D modeling and visualization | Scene creation, rendering, geometric operations |
| **physical_management** | Physical system simulation | Hardware monitoring, resource management |
| **system_discovery** | System exploration | Module discovery, capability detection, health monitoring |

## Project Structure

```
codomyrmex/
├── src/codomyrmex/          # Core source modules
│   ├── ai_code_editing/     # AI-powered code assistance
│   ├── static_analysis/     # Code quality analysis
│   ├── logging_monitoring/  # Centralized logging
│   └── ...                  # 25+ additional modules
├── scripts/                 # Maintenance and automation utilities
│   ├── documentation/       # Documentation maintenance scripts
│   ├── development/         # Development utilities
│   ├── examples/            # Example scripts and demonstrations
│   └── ...                  # 35+ module orchestrators
├── docs/                    # Project documentation
│   ├── getting-started/     # Installation and quickstart guides
│   ├── modules/             # Module system documentation
│   ├── project/             # Architecture and contributing guides
│   └── reference/           # API reference and troubleshooting
├── testing/                 # Test suites
│   ├── unit/                # Unit tests
│   └── integration/         # Integration tests
├── config/                  # Configuration templates and examples
│   ├── examples/            # Configuration examples
│   └── templates/           # Configuration templates
├── cursorrules/             # Coding standards and automation rules
│   ├── modules/             # Module-specific rules
│   ├── cross-module/        # Cross-module coordination rules
│   └── file-specific/       # File-specific rules
├── projects/                # Project workspace and templates
│   └── test_project/        # Example project structure
├── examples/                # Example scripts and demonstrations
├── src/template/            # Code generation templates
└── @output/                 # Generated output and reports
```

## Key Concepts

### Modular Architecture
Each module is self-contained with:
- Own dependencies (`requirements.txt`)
- Comprehensive tests (`tests/`)
- API documentation (`API_SPECIFICATION.md`)
- Usage examples (`USAGE_EXAMPLES.md`)
- Security considerations (`SECURITY.md`)

### Model Context Protocol (MCP)
Standardized interface for AI integration:
- Tool specifications for LLM interactions
- Consistent parameter schemas
- Provider-agnostic design
- Full documentation in each module's `MCP_TOOL_SPECIFICATION.md`

### Layered Dependencies
Modules organized to prevent circular dependencies:
- **Foundation Layer**: Base services (logging, environment, terminal)
- **Core Layer**: Functional capabilities (analysis, execution, visualization)
- **Service Layer**: Orchestration and integration
- **Application Layer**: User interfaces (CLI, interactive shell)

## Documentation

- **[Getting Started Guide](docs/getting-started/quickstart.md)** - Quick introduction and setup
- **[Architecture Overview](docs/project/architecture.md)** - System design and principles
- **[Module System](docs/modules/overview.md)** - Module architecture and relationships
- **[Contributing Guide](docs/project/contributing.md)** - Development guidelines
- **[API Reference](docs/reference/api.md)** - Complete API documentation
- **[Troubleshooting](docs/reference/troubleshooting.md)** - Common issues and solutions

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/codomyrmex --cov-report=html

# Run specific test suite
pytest testing/unit/
pytest testing/integration/
```

### Code Quality

```bash
# Format code
black src/ testing/

# Lint code
ruff check src/ testing/

# Type checking
mypy src/
```

### Module Development

See **[Creating a Module Tutorial](docs/getting-started/tutorials/creating-a-module.md)** for detailed guidance on developing new modules.

## Contributing

We welcome contributions! Please see our **[Contributing Guide](docs/project/contributing.md)** for:
- Code standards and best practices
- Development workflow
- Pull request process
- Testing requirements
- Documentation guidelines

## Security

Security is a priority. See **[SECURITY.md](SECURITY.md)** for:
- Vulnerability reporting
- Security best practices
- Module-specific security considerations

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

Copyright (c) 2025 The Codomyrmex Contributors (@docxology)

## Links

- **Repository**: [github.com/codomyrmex/codomyrmex](https://github.com/codomyrmex/codomyrmex)
- **Issues**: [github.com/codomyrmex/codomyrmex/issues](https://github.com/codomyrmex/codomyrmex/issues)
- **Documentation**: [codomyrmex.readthedocs.io](https://codomyrmex.readthedocs.io/)

---

**Built with a focus on modularity, clarity, and professional development practices.**
