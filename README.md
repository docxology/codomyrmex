# Codomyrmex

**Version**: v1.0.3 | **Status**: Active | **Last Updated**: February 2026
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-≥3.10-blue.svg)](https://www.python.org/downloads/)
[![Version](https://img.shields.io/badge/version-1.0.3-blue.svg)](https://github.com/docxology/codomyrmex)
[![Tests](https://img.shields.io/badge/tests-15,179%20passing-brightgreen.svg)](https://github.com/docxology/codomyrmex)
[![Coverage](https://img.shields.io/badge/coverage-~68%25-blue.svg)](https://github.com/docxology/codomyrmex)

> **A modular, extensible coding workspace designed for AI development workflows**

Codomyrmex integrates tools for building, documenting, analyzing, executing, and visualizing code across multiple languages. Built with modularity and AI integration at its core, it provides a comprehensive platform for modern software development.

## What is Codomyrmex?

Codomyrmex is a **modular development platform** that brings together 88 specialized modules for code analysis, AI-assisted development, build automation, documentation, and more. Each module is self-contained, tested, and can be used independently or composed together for complex workflows.

### Key Features

- **AI-Powered Development** - Built-in support for Large Language Models via Model Context Protocol (MCP)
- **Modular Architecture** - 88 independent, composable modules with clear interfaces
- **Code Analysis** - Static analysis, pattern matching, security scanning, and quality metrics
- **Build & Deploy** - Multi-language builds, CI/CD automation, container management
- **Visualization** - Data visualization, 3D/4D spatial modeling, and interactive plots
- **Documentation** - Automated documentation generation, API specs, and tutorials
- **Security First** - Built-in security scanning, vulnerability detection, and compliance checking
- **Polyglot Support** - Language-agnostic interfaces supporting Python, JavaScript, Go, Rust, Java

### Why Codomyrmex?

- **Modularity First**: Self-contained modules with clear boundaries - use what you need, when you need it
- **AI Integration**: Seamless integration with LLMs through standardized Model Context Protocol
- **Tested**: Over ten thousand unit, integration, and workflow tests exercise core functionality across modules
- **Well-Documented**: RASP documentation (README, AGENTS, SPEC, PAI) and API references for modules and tools
- **Robust Interfaces**: Stable public APIs with structured error handling and telemetry

## Quick Start

Get started with Codomyrmex in minutes:

```bash
# Clone the repository
git clone https://github.com/docxology/codomyrmex.git
cd codomyrmex

# Install with uv (recommended)
uv sync

# Launch interactive shell
./start_here.sh
```

**New to Codomyrmex?** Start with the [Quick Start Guide](docs/getting-started/quickstart.md) or explore [executable examples](scripts/documentation/examples/).

## Documentation Hub

Codomyrmex documentation is organized into focused guides for different needs:

### Getting Started

| Guide | Description |
|-------|-------------|
| [**Quick Start**](docs/getting-started/quickstart.md) | Get up and running in 5 minutes |
| [**Installation**](docs/getting-started/installation.md) | Detailed installation instructions |
| [**Setup**](docs/getting-started/setup.md) | Environment configuration |
| [**Tutorials**](docs/getting-started/tutorials/) | Step-by-step learning paths |

### Architecture & Design

| Guide | Description |
|-------|-------------|
| [**Architecture**](docs/project/architecture.md) | System design and principles |
| [**Full Setup Guide**](docs/getting-started/full-setup.md) | Complete architecture, module tables, and development guide |
| [**Module Overview**](docs/modules/overview.md) | Understanding the module system |
| [**Contributing**](docs/project/contributing.md) | How to contribute to Codomyrmex |
| [**Project Roadmap**](docs/project/README.md) | Current priorities and future plans |

### Development

| Guide | Description |
|-------|-------------|
| [**Environment Setup**](docs/development/environment-setup.md) | Development environment configuration |
| [**Testing Strategy**](docs/development/testing-strategy.md) | Testing approach and best practices |
| [**Documentation Guide**](docs/development/documentation.md) | Writing documentation |
| [**uv Usage Guide**](docs/development/uv-usage-guide.md) | Package management with uv |

### Reference

| Guide | Description |
|-------|-------------|
| [**API Reference**](docs/reference/api.md) | Complete API documentation |
| [**CLI Reference**](docs/reference/cli.md) | Command-line interface |
| [**Orchestrator**](docs/reference/orchestrator.md) | Workflow orchestration |
| [**Performance**](docs/reference/performance.md) | Performance optimization |
| [**Troubleshooting**](docs/reference/troubleshooting.md) | Common issues and solutions |

### Deployment & Operations

| Guide | Description |
|-------|-------------|
| [**Production Deployment**](docs/deployment/production.md) | Production deployment guide |
| [**Security**](docs/reference/security.md) | Security best practices |
| [**Migration Guide**](docs/reference/migration-guide.md) | Upgrading between versions |

### Integration

| Guide | Description |
|-------|-------------|
| [**Integration Overview**](docs/integration/) | External service integration |
| [**Examples**](docs/examples/) | Working code examples |
| [**Project Orchestration**](docs/project_orchestration/) | Multi-project workflows |

- [**AGENTS.md**](AGENTS.md) | Agent coordination protocols
- [**PAI.md**](PAI.md) | Personal AI Infrastructure
- [**SPEC.md**](SPEC.md) | Functional specification

## Examples & Tutorials

Codomyrmex provides comprehensive examples to help you get started quickly:

### Hands-on Examples

- [**Basic Usage**](scripts/documentation/examples/basic_usage.py) - Core module interactions
- [**Advanced Workflows**](scripts/documentation/examples/advanced_workflow.py) - Multi-module orchestration
- [**Agent Demos**](src/codomyrmex/agents/ai_code_editing/README.md#examples) - AI-assisted coding examples

### Executable Demos

Run these from the root using `uv run python`:

```bash
uv run scripts/documentation/examples/basic_usage.py
uv run scripts/documentation/examples/advanced_workflow.py
```

---

**Quick Links:**

- [Source Code](src/codomyrmex/README.md) - Browse all modules
- [Full Documentation](docs/) - Complete documentation
- [Module Documentation](docs/modules/) - Per-module guides
- [Scripts](scripts/) - Utility and automation scripts

## Core Modules at a Glance

| Category | Key Modules |
| :--- | :--- |
| **Foundation** | [logging_monitoring](src/codomyrmex/logging_monitoring/) - [environment_setup](src/codomyrmex/environment_setup/) - [model_context_protocol](src/codomyrmex/model_context_protocol/) - [terminal_interface](src/codomyrmex/terminal_interface/) |
| **Core** | [agents](src/codomyrmex/agents/) - [coding](src/codomyrmex/coding/) - [llm](src/codomyrmex/llm/) - [security](src/codomyrmex/security/) - [git_operations](src/codomyrmex/git_operations/) - [data_visualization](src/codomyrmex/data_visualization/) |
| **Service** | [documentation](src/codomyrmex/documentation/) - [api](src/codomyrmex/api/) - [ci_cd_automation](src/codomyrmex/ci_cd_automation/) - [containerization](src/codomyrmex/containerization/) - [orchestrator](src/codomyrmex/orchestrator/) |
| **Specialized** | [spatial](src/codomyrmex/spatial/) - [cerebrum](src/codomyrmex/cerebrum/) - [events](src/codomyrmex/events/) - [plugin_system](src/codomyrmex/plugin_system/) - [agentic_memory](src/codomyrmex/agentic_memory/) |

See the **[Full Setup Guide](docs/getting-started/full-setup.md)** for complete module tables, architecture diagrams, and the module quick reference.

## Development

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src/codomyrmex --cov-report=html

# Run specific test suite
uv run pytest src/codomyrmex/tests/unit/
```

### Code Quality

```bash
# Format code
uv run black src/

# Lint code
uv run ruff check src/

# Type checking
uv run mypy src/
```

### Module Development

See **[Creating a Module Tutorial](docs/getting-started/tutorials/creating-a-module.md)** for detailed guidance on developing new modules.

## Key Metrics

- **Lines of Code**: ~100K+ across 88 modules
- **Test Coverage**: ~68% (15,179 tests passing, gate: 67%)
- **Module Count**: 88 modules (88 load successfully; 6 additional require optional SDKs)
- **Language Support**: Python, JavaScript, Go, Rust, Java
- **AI Integration**: 5+ LLM providers supported
- **Documentation**: 200+ pages across all modules

## Contributing

We welcome contributions! Please see our **[Contributing Guide](docs/project/contributing.md)** for code standards, development workflow, pull request process, and testing requirements.

## Security

Security is a priority. See **[SECURITY.md](SECURITY.md)** for vulnerability reporting, security best practices, and module-specific security considerations.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

Copyright (c) 2025 The Codomyrmex Contributors (@docxology)

## Links

- **Repository**: [github.com/docxology/codomyrmex](https://github.com/docxology/codomyrmex)
- **Issues**: [github.com/docxology/codomyrmex/issues](https://github.com/docxology/codomyrmex/issues)

---

**Built with a focus on modularity, clarity, and professional development practices.**

## Example Usage

```bash
# CLI usage (primary entry point)
codomyrmex check                 # Verify environment setup
codomyrmex modules               # List available modules
codomyrmex status                # System status dashboard
codomyrmex shell                 # Interactive shell
```

> Full documentation: [Architecture & Setup](docs/getting-started/full-setup.md) | [Module Reference](docs/getting-started/tutorials/creating-a-module.md)

## Navigation Links

- **Documentation**: [Reference Guides](docs/README.md)
- **All Agents**: [AGENTS.md](AGENTS.md)
- **Functional Spec**: [SPEC.md](SPEC.md)
- **Source Index**: [src/README.md](src/README.md)
