# Codomyrmex Source Modules

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Overview

This directory contains all core source modules for the Codomyrmex platform. Modules are organized in a layered architecture that prevents circular dependencies and ensures clean separation of concerns.

## Architecture Layers

### Foundation Layer

Essential infrastructure used by all other modules:

| Module | Purpose | Status |
| :--- | :--- | :--- |
| [logging_monitoring/](logging_monitoring/) | Centralized logging and monitoring | Production |
| [environment_setup/](environment_setup/) | Environment validation and configuration | Production |
| [model_context_protocol/](model_context_protocol/) | AI communication standards (MCP) | Production |
| [terminal_interface/](terminal_interface/) | Rich terminal interactions | Production |
| [config_management/](config_management/) | Configuration management | Production |
| [metrics/](metrics/) | Metrics collection and reporting | Beta |

### Core Layer

Primary development capabilities:

| Module | Purpose | Status |
| :--- | :--- | :--- |
| [agents/](agents/) | AI agent framework integrations | Production |
| [static_analysis/](static_analysis/) | Code quality analysis and linting | Production |
| [coding/](coding/) | Code execution, sandboxing, and review | Production |
| [data_visualization/](data_visualization/) | Charts, plots, and visualizations | Production |
| [pattern_matching/](pattern_matching/) | Code pattern recognition | Production |
| [git_operations/](git_operations/) | Git automation and workflows | Production |
| [security/](security/) | Security scanning and compliance | Production |
| [llm/](llm/) | LLM infrastructure (Ollama, Fabric) | Production |
| [performance/](performance/) | Performance profiling and benchmarking | Beta |

### Service Layer

Higher-level services orchestrating core modules:

| Module | Purpose | Status |
| :--- | :--- | :--- |
| [build_synthesis/](build_synthesis/) | Multi-language build automation | Production |
| [documentation/](documentation/) | Documentation generation | Production |
| [api/](api/) | API infrastructure and standardization | Production |
| [ci_cd_automation/](ci_cd_automation/) | CI/CD pipeline management | Production |
| [containerization/](containerization/) | Container and Kubernetes management | Beta |
| [database_management/](database_management/) | Database operations and migrations | Beta |
| [logistics/](logistics/) | Task scheduling and orchestration | Beta |
| [orchestrator/](orchestrator/) | DAG-based workflow orchestration | Beta |
| [auth/](auth/) | Authentication and authorization | Beta |
| [cloud/](cloud/) | Cloud provider integrations | Alpha |

### Specialized Layer

Advanced and domain-specific capabilities:

| Module | Purpose | Status |
| :--- | :--- | :--- |
| [cerebrum/](cerebrum/) | Case-based reasoning and Bayesian inference | Beta |
| [fpf/](fpf/) | Functional Programming Framework | Beta |
| [spatial/](spatial/) | 3D/4D spatial modeling | Alpha |
| [events/](events/) | Event system and pub/sub | Production |
| [plugin_system/](plugin_system/) | Plugin architecture | Production |
| [skills/](skills/) | Skills management system | Alpha |
| [ide/](ide/) | IDE integrations (Cursor, VSCode) | Beta |
| [tools/](tools/) | Utility tools | Production |
| [documents/](documents/) | Document processing | Beta |
| [system_discovery/](system_discovery/) | System exploration | Production |
| [module_template/](module_template/) | Module scaffolding | Production |

### Utility Modules

Supporting utilities and infrastructure:

| Module | Purpose |
| :--- | :--- |
| [utils/](utils/) | Common utility functions |
| [validation/](validation/) | Input validation |
| [serialization/](serialization/) | Data serialization |
| [compression/](compression/) | Data compression |
| [encryption/](encryption/) | Cryptographic operations |
| [networking/](networking/) | Network utilities |
| [scrape/](scrape/) | Web scraping |
| [templating/](templating/) | Template engine |
| [cache/](cache/) | Caching backends |
| [website/](website/) | Website generation |
| [cli/](cli/) | CLI utilities |

## Module Structure

Each module follows a consistent structure:

```
module_name/
├── __init__.py              # Public API exports
├── README.md                # User documentation
├── AGENTS.md                # Agent coordination
├── SPEC.md                  # Functional specification
├── API_SPECIFICATION.md     # API documentation
├── MCP_TOOL_SPECIFICATION.md # MCP tool definitions
├── USAGE_EXAMPLES.md        # Code examples
├── SECURITY.md              # Security considerations
├── CHANGELOG.md             # Version history
├── requirements.txt         # Module dependencies
├── core/                    # Core implementations
├── handlers/                # Request handlers (optional)
└── tests/                   # Test suites
```

## Quick Start

```python
# Import from any module
from codomyrmex.logging_monitoring import setup_logging, get_logger
from codomyrmex.agents import AgentOrchestrator, ClaudeClient
from codomyrmex.cerebrum import CerebrumEngine, Case
from codomyrmex.llm import OllamaManager

# Initialize logging first
setup_logging()
logger = get_logger(__name__)

# Use modules
logger.info("Codomyrmex initialized")
```

## Dependency Rules

1. **Foundation** modules have no internal dependencies
2. **Core** modules depend only on Foundation
3. **Service** modules depend on Foundation and Core
4. **Specialized** modules depend on Foundation, Core, and Service
5. No circular dependencies allowed

## Testing

```bash
# Run all tests
uv run pytest src/codomyrmex/tests/

# Run specific module tests
uv run pytest src/codomyrmex/agents/tests/
uv run pytest src/codomyrmex/cerebrum/tests/

# With coverage
uv run pytest --cov=src/codomyrmex --cov-report=html
```

## Signposting

### Navigation

- **Self**: [README.md](README.md)
- **Parent**: [src/](../README.md)
- **Project Root**: [../../README.md](../../README.md)

### Key Documentation

- [AGENTS.md](AGENTS.md) - Agent coordination hub
- [SPEC.md](SPEC.md) - Functional specification
- [../../../docs/modules/overview.md](../../docs/modules/overview.md) - Module system documentation

### Module Documentation Index

| Layer | Modules |
| :--- | :--- |
| Foundation | [logging_monitoring](logging_monitoring/), [environment_setup](environment_setup/), [model_context_protocol](model_context_protocol/), [terminal_interface](terminal_interface/) |
| Core | [agents](agents/), [static_analysis](static_analysis/), [coding](coding/), [llm](llm/), [git_operations](git_operations/) |
| Service | [build_synthesis](build_synthesis/), [documentation](documentation/), [api](api/), [orchestrator](orchestrator/) |
| Specialized | [cerebrum](cerebrum/), [fpf](fpf/), [spatial](spatial/), [events](events/) |
