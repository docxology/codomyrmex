# Module Documentation

**Version**: v1.0.5 | **Status**: Active | **Last Updated**: March 2026

## Overview

Comprehensive documentation for all Codomyrmex modules. Each module has its own subdirectory with detailed documentation, API specifications, and usage examples.

> [!NOTE]
> In v0.1.1, 28 thin and overlapping modules were consolidated into their natural host modules. See the consolidation table below for the new canonical locations.

## Key Documentation Files

| File | Description |
|------|-------------|
| [**overview.md**](overview.md) | Complete module system overview |
| [**relationships.md**](relationships.md) | Inter-module dependencies and data flow |
| [**dependency-graph.md**](dependency-graph.md) | Visual dependency graph |
| [**ollama.md**](ollama.md) | Local LLM integration guide |

## Module Categories

### Foundation Modules

Core infrastructure used by all other modules.

| Module | Description |
|--------|-------------|
| [cache/](cache/) | In-memory and distributed caching, invalidation strategies |
| [compression/](compression/) | Data compression utilities |
| [concurrency/](concurrency/) | Distributed locks, semaphores, channels, and rate limiting |
| [config_management/](config_management/) | Configuration management |
| [database_management/](database_management/) | Data persistence, backup, migration, and lineage tracking |
| [encryption/](encryption/) | Encryption, cryptographic utilities, and digital signing |
| [environment_setup/](environment_setup/) | Development environment validation and dependency resolution |
| [events/](events/) | Event-driven architecture: pub/sub, replay, dead letter, streaming, notifications |
| [logging_monitoring/](logging_monitoring/) | Centralized logging and monitoring |
| [serialization/](serialization/) | Data serialization formats and streaming I/O |
| [telemetry/](telemetry/) | OpenTelemetry observability, metrics collection, and dashboards |
| [validation/](validation/) | Data and schema validation, shared schema registry |

### AI & Intelligence Modules

AI-powered capabilities for code generation and analysis.

| Module | Description |
|--------|-------------|
| [agentic_memory/](agentic_memory/) | Long-term agent memory with retrieval, persistence, and compression |
| [agents/](agents/) | AI agent framework (Claude, Codex, Gemini, Jules, Mistral) with benchmarks |
| [cerebrum/](cerebrum/) | Case-based reasoning and Bayesian inference |
| [graph_rag/](graph_rag/) | Knowledge graph-enhanced RAG |
| [llm/](llm/) | LLM provider abstraction, Ollama support, multimodal, and safety filtering |
| [model_context_protocol/](model_context_protocol/) | MCP implementation, tool discovery, and standardized LLM interfaces |
| [model_ops/](model_ops/) | ML model operations, evaluation, registry, optimization, and feature store |
| [prompt_engineering/](prompt_engineering/) | Prompt template management, versioning, optimization, and testing |
| [vector_store/](vector_store/) | Embeddings storage with similarity search |

### Code & Analysis Modules

Code analysis and pattern recognition.

| Module | Description |
|--------|-------------|
| [coding/](coding/) | Safe code execution, static analysis, and pattern matching |
| [formal_verification/](formal_verification/) | Model checking, theorem proving, and formal proofs |
| [static_analysis/](static_analysis/) | Static analysis and code parsing |
| [tree_sitter/](tree_sitter/) | Tree-sitter grammar and AST utilities |

### Data & Visualization Modules

Data management and visualization.

| Module | Description |
|--------|-------------|
| [data_visualization/](data_visualization/) | Charts, plots, and multi-format export |
| [git_analysis/](git_analysis/) | Git history analysis, commit patterns, and repository health |
| [search/](search/) | Full-text search with TF-IDF, fuzzy matching, and hybrid BM25+semantic |

### DevOps & Infrastructure Modules

Build, deployment, and infrastructure management.

| Module | Description |
|--------|-------------|
| [ci_cd_automation/](ci_cd_automation/) | CI/CD pipeline management and build automation |
| [cloud/](cloud/) | Cloud provider integration and cost management |
| [containerization/](containerization/) | Docker/Kubernetes management |
| [dependency_injection/](dependency_injection/) | IoC container, service registration, lifecycle scoping |
| [deployment/](deployment/) | Deployment strategies and orchestration |
| [edge_computing/](edge_computing/) | Edge deployment and IoT gateways |
| [docs_gen/](docs_gen/) | Documentation template scaffolding and source-to-docs conversion |
| [git_operations/](git_operations/) | Git workflow automation and merge conflict resolution |
| [networking/](networking/) | Network utilities and service mesh |
| [orchestrator/](orchestrator/) | Workflow execution engine and scheduling |
| [performance/](performance/) | Performance profiling and benchmarking |
| [release/](release/) | Versioning, changelog generation, and release coordination |
| [testing/](testing/) | Test fixtures, generators, workflow testing, and chaos engineering |

### Security & Cognitive Modules

Autonomous security and economic capabilities.

| Module | Description |
|--------|-------------|
| [auth/](auth/) | Authentication and authorization |
| [dark/](dark/) | Dark mode utilities and PDF processing |
| [crypto/](crypto/) | Cryptography utilities and protocols |
| [defense/](defense/) | Active defense systems |
| [identity/](identity/) | 3-Tier personas, bio-verification |
| [market/](market/) | Reverse auctions, demand aggregation |
| [privacy/](privacy/) | Crumb scrubbing, mixnet routing |
| [security/](security/) | Security scanning, hardening, vulnerability scanning, and governance |
| [wallet/](wallet/) | Self-custody, Natural Ritual recovery, and smart contracts |

### Interface & Communication Modules

User interfaces and communication channels.

| Module | Description |
|--------|-------------|
| [api/](api/) | REST/GraphQL API framework with rate limiting |
| [audio/](audio/) | Audio processing and transcription |
| [calendar_integration/](calendar_integration/) | Calendar providers, event scheduling (Google Calendar) |
| [cli/](cli/) | Command-line interface with shell completion |
| [collaboration/](collaboration/) | Multi-agent collaboration and swarm coordination |
| [documents/](documents/) | Document processing and RAG chunking |
| [email/](email/) | Email communication (Gmail, AgentMail) |
| [fpf/](fpf/) | File processing framework |
| [ide/](ide/) | IDE integration |
| [skills/](skills/) | Skill management system |
| [terminal_interface/](terminal_interface/) | Rich terminal formatting |
| [video/](video/) | Video processing and analysis |
| [website/](website/) | Web content management and accessibility |

### Framework & Utilities Modules

Supporting utilities and infrastructure.

| Module | Description |
|--------|-------------|
| [bio_simulation/](bio_simulation/) | Ant colony simulation, pheromone foraging, genetic algorithms |
| [crypto/](crypto/) | Cryptography utilities, protocols, and steganography |
| [documentation/](documentation/) | Documentation generation and education |
| [embodiment/](embodiment/) | Physical/robotic system integration |
| [evolutionary_ai/](evolutionary_ai/) | Genetic algorithms and optimization |
| [examples/](examples/) | Code examples and templates |
| [exceptions/](exceptions/) | Centralized exception hierarchy and error handling |
| [feature_flags/](feature_flags/) | Feature toggle management |
| [finance/](finance/) | Double-entry bookkeeping, tax compliance, payroll, forecasting |
| [logistics/](logistics/) | Logistics and supply chain |
| [maintenance/](maintenance/) | System maintenance and health checks |
| [meme/](meme/) | Memetic warfare, information dynamics, meme propagation |
| [module_template/](module_template/) | Module scaffolding template |
| [physical_management/](physical_management/) | Physical asset management |
| [plugin_system/](plugin_system/) | Plugin architecture |
| [quantum/](quantum/) | Quantum algorithm primitives and circuit simulation |
| [relations/](relations/) | Entity relationship management |
| [scrape/](scrape/) | Web scraping utilities |
| [simulation/](simulation/) | General simulation framework, agent-based modeling |
| [spatial/](spatial/) | Spatial data processing |
| [system_discovery/](system_discovery/) | Module discovery and health monitoring |
| [templating/](templating/) | Template rendering engine |
| [tests/](tests/) | Project test suite |
| [tool_use/](tool_use/) | Tool registry, composition, and validation for workflows |
| [utils/](utils/) | General utilities, hashing, retry, and i18n |

## v0.1.1 Module Consolidation Map

The following modules have been absorbed into their host modules:

| Former Module | Now Located In |
|---------------|---------------|
| `metrics` | `telemetry/metrics/` |
| `telemetry` | `telemetry/dashboard/` |
| `static_analysis` | `coding/static_analysis/` |
| `pattern_matching` | `coding/pattern_matching/` |
| `visualization` | `data_visualization/` |
| `model_evaluation` | `model_ops/evaluation/` |
| `model_ops` | `model_ops/registry/` |
| `performance` | `model_ops/optimization/` |
| `prompt_engineering` | `prompt_engineering/testing/` |
| `testing` | `testing/workflow/` |
| `chaos_engineering` | `testing/chaos/` |
| `rate_limiting` | `api/rate_limiting/` |
| `deployment` | `ci_cd_automation/build/` |
| `scheduler` | `orchestrator/scheduler/` |
| `streaming` | `events/streaming/` |
| `service_mesh` | `networking/service_mesh/` |
| `migration` | `database_management/migration/` |
| `schemas` | `validation/schemas/` |
| `performance` | `cloud/performance/` |
| `telemetry` | `database_management/lineage/` |
| `vector_store` | `model_ops/vector_store/` |
| `i18n` | `utils/i18n/` |
| `accessibility` | `website/accessibility/` |
| `education` | `documentation/education/` |
| `multimodal` | `llm/multimodal/` |
| `notification` | `events/notification/` |
| `smart_contracts` | `wallet/contracts/` |
| `governance` | `security/governance/` |

## Module Documentation Standard

Each module directory contains:

- `README.md` - Human-readable overview
- `AGENTS.md` - Agent coordination
- `SPEC.md` - Functional specification
- `PAI.md` - Personal AI considerations
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
