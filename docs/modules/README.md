# Module Documentation

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Comprehensive documentation for all 81 Codomyrmex modules. Each module has its own subdirectory with detailed documentation, API specifications, and usage examples.

## Key Documentation Files

| File | Description |
|------|-------------|
| [**overview.md**](overview.md) | Complete module system overview |
| [**relationships.md**](relationships.md) | Inter-module dependencies and data flow |
| [**dependency-graph.md**](dependency-graph.md) | Visual dependency graph |
| [**ollama_integration.md**](ollama_integration.md) | Local LLM integration guide |

## Module Categories

### Foundation Modules

Core infrastructure used by all other modules.

| Module | Description |
|--------|-------------|
| [cache/](cache/) | In-memory and distributed caching |
| [compression/](compression/) | Data compression utilities |
| [concurrency/](concurrency/) | Distributed locks, semaphores, and synchronization |
| [config_management/](config_management/) | Configuration management |
| [database_management/](database_management/) | Data persistence |
| [encryption/](encryption/) | Encryption and cryptographic utilities |
| [environment_setup/](environment_setup/) | Development environment validation |
| [events/](events/) | Event-driven architecture primitives |
| [logging_monitoring/](logging_monitoring/) | Centralized logging and monitoring |
| [serialization/](serialization/) | Data serialization formats |
| [telemetry/](telemetry/) | OpenTelemetry-based observability |
| [validation/](validation/) | Data and schema validation |

### AI & Intelligence Modules

AI-powered capabilities for code generation and analysis.

| Module | Description |
|--------|-------------|
| [agentic_memory/](agentic_memory/) | Long-term agent memory with retrieval and persistence |
| [agents/](agents/) | AI agent framework (Claude, Codex, Gemini, Jules, Mistral) |
| [cerebrum/](cerebrum/) | Case-based reasoning and Bayesian inference |
| [graph_rag/](graph_rag/) | Knowledge graph-enhanced RAG |
| [inference_optimization/](inference_optimization/) | Model quantization, batching, and caching |
| [llm/](llm/) | LLM provider abstraction and Ollama support |
| [model_context_protocol/](model_context_protocol/) | MCP implementation and standardized LLM interfaces |
| [model_ops/](model_ops/) | ML model operations and evaluation |
| [model_registry/](model_registry/) | Model versioning and lifecycle management |
| [multimodal/](multimodal/) | Vision, audio, and image processing |
| [prompt_testing/](prompt_testing/) | Prompt evaluation and A/B testing |

### Code & Analysis Modules

Code analysis and pattern recognition.

| Module | Description |
|--------|-------------|
| [coding/](coding/) | Safe code execution sandbox |
| [pattern_matching/](pattern_matching/) | Code pattern recognition |
| [static_analysis/](static_analysis/) | Code quality analysis |
| [tree_sitter/](tree_sitter/) | AST parsing and analysis |

### Data & Visualization Modules

Data management and visualization.

| Module | Description |
|--------|-------------|
| [data_lineage/](data_lineage/) | Data provenance and lineage tracking |
| [data_visualization/](data_visualization/) | Charts and plots |
| [feature_store/](feature_store/) | Feature management for ML pipelines |

### DevOps & Infrastructure Modules

Build, deployment, and infrastructure management.

| Module | Description |
|--------|-------------|
| [build_synthesis/](build_synthesis/) | Build automation |
| [ci_cd_automation/](ci_cd_automation/) | CI/CD pipeline management |
| [cloud/](cloud/) | Cloud provider integration |
| [containerization/](containerization/) | Docker/Kubernetes management |
| [cost_management/](cost_management/) | Infrastructure and LLM cost tracking |
| [deployment/](deployment/) | Deployment strategies and orchestration |
| [git_operations/](git_operations/) | Git workflow automation |
| [migration/](migration/) | Cross-provider migration tools |
| [observability_dashboard/](observability_dashboard/) | Unified monitoring dashboards |
| [orchestrator/](orchestrator/) | Workflow execution engine |
| [performance/](performance/) | Performance profiling and benchmarking |
| [workflow_testing/](workflow_testing/) | End-to-end workflow validation |

### Security & Cognitive Modules

Autonomous security and economic capabilities.

| Module | Description |
|--------|-------------|
| [dark/](dark/) | Dark mode utilities and PDF processing |
| [defense/](defense/) | Active defense systems |
| [identity/](identity/) | 3-Tier personas, bio-verification |
| [market/](market/) | Reverse auctions, demand aggregation |
| [privacy/](privacy/) | Crumb scrubbing, mixnet routing |
| [security/](security/) | Security scanning and hardening |
| [wallet/](wallet/) | Self-custody, Natural Ritual recovery |

### Interface & Communication Modules

User interfaces and communication channels.

| Module | Description |
|--------|-------------|
| [api/](api/) | REST/GraphQL API framework |
| [audio/](audio/) | Audio processing and transcription |
| [cli/](cli/) | Command-line interface |
| [collaboration/](collaboration/) | Multi-agent collaboration and swarm coordination |
| [documents/](documents/) | Document processing |
| [fpf/](fpf/) | File processing framework |
| [ide/](ide/) | IDE integration |
| [notification/](notification/) | Multi-channel notification dispatch |
| [skills/](skills/) | Skill management system |
| [terminal_interface/](terminal_interface/) | Rich terminal formatting |
| [video/](video/) | Video processing and analysis |
| [website/](website/) | Web content management |

### Framework & Utilities Modules

Supporting utilities and infrastructure.

| Module | Description |
|--------|-------------|
| [auth/](auth/) | Authentication and authorization |
| [documentation/](documentation/) | Documentation generation |
| [embodiment/](embodiment/) | Physical/robotic system integration |
| [evolutionary_ai/](evolutionary_ai/) | Genetic algorithms and optimization |
| [examples/](examples/) | Code examples and templates |
| [feature_flags/](feature_flags/) | Feature toggle management |
| [logistics/](logistics/) | Logistics and supply chain |
| [metrics/](metrics/) | Metrics collection and aggregation |
| [module_template/](module_template/) | Module scaffolding template |
| [networking/](networking/) | Network utilities |
| [physical_management/](physical_management/) | Physical asset management |
| [plugin_system/](plugin_system/) | Plugin architecture |
| [scrape/](scrape/) | Web scraping utilities |
| [spatial/](spatial/) | Spatial data processing |
| [system_discovery/](system_discovery/) | Module discovery and health monitoring |
| [templating/](templating/) | Template rendering engine |
| [testing/](testing/) | Test fixtures and data generators |
| [tests/](tests/) | Project test suite |
| [tools/](tools/) | Development tools |
| [utils/](utils/) | General utilities |

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
- **Agent Coordination**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
