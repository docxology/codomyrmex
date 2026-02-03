# Module Documentation

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Comprehensive documentation for all 70+ Codomyrmex modules. Each module has its own subdirectory with detailed documentation, API specifications, and usage examples.

## Key Documentation Files

| File | Description |
|------|-------------|
| [**overview.md**](overview.md) | Complete module system overview |
| [**relationships.md**](relationships.md) | Inter-module dependencies and data flow |
| [**dependency-graph.md**](dependency-graph.md) | Visual dependency graph |
| [**ollama_integration.md**](ollama_integration.md) | Local LLM integration guide |

## Module Categories

### 🏗️ Foundation Modules

Core infrastructure used by all other modules.

| Module | Description |
|--------|-------------|
| [logging_monitoring/](logging_monitoring/) | Centralized logging and monitoring |
| [environment_setup/](environment_setup/) | Development environment validation |
| [config_management/](config_management/) | Configuration management |
| [database_management/](database_management/) | Data persistence |

### 🤖 AI & Intelligence Modules

AI-powered capabilities for code generation and analysis.

| Module | Description |
|--------|-------------|
| [agents/](agents/) | AI agent framework |
| [cerebrum/](cerebrum/) | Reasoning and memory |
| [llm/](llm/) | LLM provider abstraction |
| [model_context_protocol/](model_context_protocol/) | MCP implementation |

### 📊 Analysis & Visualization Modules

Code analysis and data presentation.

| Module | Description |
|--------|-------------|
| [static_analysis/](static_analysis/) | Code quality analysis |
| [pattern_matching/](pattern_matching/) | Code pattern recognition |
| [data_visualization/](data_visualization/) | Charts and plots |
| [coding/](coding/) | Safe code execution |

### 🛡️ Secure Cognitive Modules

Autonomous security and economic capabilities.

| Module | Description |
|--------|-------------|
| [identity/](../../src/codomyrmex/identity/) | 3-Tier persona management |
| [wallet/](../../src/codomyrmex/wallet/) | Self-custody and recovery |
| [defense/](../../src/codomyrmex/defense/) | Active defense systems |
| [market/](../../src/codomyrmex/market/) | Anonymous markets |
| [privacy/](../../src/codomyrmex/privacy/) | Mixnet and crumb scrubbing |

### 🔧 Utility Modules

Supporting utilities and infrastructure.

| Module | Description |
|--------|-------------|
| [cli/](cli/) | Command-line interface |
| [terminal_interface/](terminal_interface/) | Rich terminal formatting |
| [git_operations/](git_operations/) | Git workflow automation |
| [build_synthesis/](build_synthesis/) | Build automation |

## Module Documentation Standard

Each module directory contains:

- `README.md` - Human-readable overview
- `AGENTS.md` - Agent coordination
- `SPEC.md` - Functional specification
- (Optional) Additional guides and tutorials

## Related Documentation

- [Architecture](../project/architecture.md) - System architecture
- [API Reference](../reference/api.md) - Complete API documentation
- [Examples](../examples/) - Code examples

## Navigation

- **Parent**: [docs/](../README.md)
- **Root**: [Project Root](../../README.md)
