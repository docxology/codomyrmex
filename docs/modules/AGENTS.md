# Codomyrmex Agents — docs/modules

## Signposting

- **Parent**: [docs](../AGENTS.md)
- **Self**: [docs/modules Agents](AGENTS.md)
- **Children** (81 modules):
    - [agentic_memory/](agentic_memory/AGENTS.md), [agents/](agents/AGENTS.md), [api/](api/AGENTS.md), [audio/](audio/AGENTS.md), [auth/](auth/AGENTS.md), [build_synthesis/](build_synthesis/AGENTS.md), [cache/](cache/AGENTS.md), [cerebrum/](cerebrum/AGENTS.md), [ci_cd_automation/](ci_cd_automation/AGENTS.md), [cli/](cli/AGENTS.md), [cloud/](cloud/AGENTS.md), [coding/](coding/AGENTS.md), [collaboration/](collaboration/AGENTS.md), [compression/](compression/AGENTS.md), [concurrency/](concurrency/AGENTS.md), [config_management/](config_management/AGENTS.md), [containerization/](containerization/AGENTS.md), [cost_management/](cost_management/AGENTS.md), [dark/](dark/AGENTS.md), [data_lineage/](data_lineage/AGENTS.md), [data_visualization/](data_visualization/AGENTS.md), [database_management/](database_management/AGENTS.md), [defense/](defense/AGENTS.md), [deployment/](deployment/AGENTS.md), [documentation/](documentation/AGENTS.md), [documents/](documents/AGENTS.md), [embodiment/](embodiment/AGENTS.md), [encryption/](encryption/AGENTS.md), [environment_setup/](environment_setup/AGENTS.md), [events/](events/AGENTS.md), [evolutionary_ai/](evolutionary_ai/AGENTS.md), [examples/](examples/AGENTS.md), [feature_flags/](feature_flags/AGENTS.md), [feature_store/](feature_store/AGENTS.md), [fpf/](fpf/AGENTS.md), [git_operations/](git_operations/AGENTS.md), [graph_rag/](graph_rag/AGENTS.md), [ide/](ide/AGENTS.md), [identity/](identity/AGENTS.md), [inference_optimization/](inference_optimization/AGENTS.md), [llm/](llm/AGENTS.md), [logging_monitoring/](logging_monitoring/AGENTS.md), [logistics/](logistics/AGENTS.md), [market/](market/AGENTS.md), [metrics/](metrics/AGENTS.md), [migration/](migration/AGENTS.md), [model_context_protocol/](model_context_protocol/AGENTS.md), [model_ops/](model_ops/AGENTS.md), [model_registry/](model_registry/AGENTS.md), [module_template/](module_template/AGENTS.md), [multimodal/](multimodal/AGENTS.md), [networking/](networking/AGENTS.md), [notification/](notification/AGENTS.md), [observability_dashboard/](observability_dashboard/AGENTS.md), [orchestrator/](orchestrator/AGENTS.md), [pattern_matching/](pattern_matching/AGENTS.md), [performance/](performance/AGENTS.md), [physical_management/](physical_management/AGENTS.md), [plugin_system/](plugin_system/AGENTS.md), [privacy/](privacy/AGENTS.md), [prompt_testing/](prompt_testing/AGENTS.md), [scrape/](scrape/AGENTS.md), [security/](security/AGENTS.md), [serialization/](serialization/AGENTS.md), [skills/](skills/AGENTS.md), [spatial/](spatial/AGENTS.md), [static_analysis/](static_analysis/AGENTS.md), [system_discovery/](system_discovery/AGENTS.md), [telemetry/](telemetry/AGENTS.md), [templating/](templating/AGENTS.md), [terminal_interface/](terminal_interface/AGENTS.md), [testing/](testing/AGENTS.md), [tests/](tests/AGENTS.md), [tools/](tools/AGENTS.md), [tree_sitter/](tree_sitter/AGENTS.md), [utils/](utils/AGENTS.md), [validation/](validation/AGENTS.md), [video/](video/AGENTS.md), [wallet/](wallet/AGENTS.md), [website/](website/AGENTS.md), [workflow_testing/](workflow_testing/AGENTS.md)
- **Key Artifacts**:
    - [Functional Spec](SPEC.md)
    - [Human Readme](README.md)
    - [Module Overview](overview.md)
    - [Module Relationships](relationships.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Purpose

Comprehensive documentation hub for all 81 Codomyrmex modules. Provides API specifications, usage guides, tutorials, and integration patterns for every module in the system.

## Active Components

- `overview.md` - Complete module system overview and architecture
- `relationships.md` - Inter-module dependencies and data flow
- `dependency-graph.md` - Visual dependency graph (Mermaid)
- `ollama_integration.md` - Local LLM integration guide
- `PAI.md` - Personal AI Infrastructure context
- 81 module subdirectories (see Module Categories below)

## Key Documentation Files

| File | Description | Priority |
|------|-------------|----------|
| [overview.md](overview.md) | Complete module system overview | High |
| [relationships.md](relationships.md) | Inter-module dependencies | High |
| [dependency-graph.md](dependency-graph.md) | Visual dependency graph | Medium |
| [ollama_integration.md](ollama_integration.md) | Local LLM integration | Medium |

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

> **Source**: [src/codomyrmex/identity/](../../src/codomyrmex/identity/), [src/codomyrmex/wallet/](../../src/codomyrmex/wallet/), [src/codomyrmex/defense/](../../src/codomyrmex/defense/), [src/codomyrmex/market/](../../src/codomyrmex/market/), [src/codomyrmex/privacy/](../../src/codomyrmex/privacy/)

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

## Documentation Coverage

All 81 modules have the complete documentation triad: README.md + AGENTS.md + SPEC.md.

## Agent Quality Standards

1. **Documentation Completeness**: Each module docs folder has README.md, AGENTS.md, SPEC.md (81/81 complete)
2. **Accuracy**: Documentation must match current source code implementations
3. **Examples**: Include working code examples for all key features
4. **Navigation**: Maintain proper links to source and related modules

## Operating Contracts

- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.
- Keep documentation synchronized with source code changes.
- Update module relationships when dependencies change.
- Record new modules in overview.md and relationships.md.
- When adding a new module subdirectory, create the full triad: README.md, AGENTS.md, SPEC.md.

## Navigation Links

- **Human Documentation**: [README.md](README.md)
- **Functional Specification**: [SPEC.md](SPEC.md)

### Directory Documentation

- **Directory Overview**: [README.md](README.md) - Complete directory documentation
- **Module Overview**: [overview.md](overview.md) - Module system architecture
- **Relationships**: [relationships.md](relationships.md) - Inter-module dependencies

### Platform Navigation

- **Parent Directory**: [docs/](../README.md) - Parent directory documentation
- **Project Root**: [README](../../README.md) - Main project documentation
- **Source Root**: [src/codomyrmex/](../../src/codomyrmex/) - Source code
