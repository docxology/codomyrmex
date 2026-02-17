# Codomyrmex Agents — src/codomyrmex

**Version**: v0.1.1 | **Status**: Active | **Last Updated**: February 2026

## Purpose

Main package directory containing 78 specialized modules for the Codomyrmex platform. Provides comprehensive AI development workflow capabilities including coding, analysis, documentation, and orchestration.

## Active Components

- `PAI.md` – Personal AI Infrastructure documentation
- `README.md` – Package overview
- `SPEC.md` – Technical specification
- `__init__.py` – Package initialization with lazy imports
- `agentic_memory/` – Memory systems for AI agents
- `agents/` – Agentic framework integrations (Jules, Claude, Codex, PAI)
- `api/` – API infrastructure and resilience
- `audio/` – Audio processing and transcription
- `auth/` – Authentication and authorization
- `bio_simulation/` – Biological simulation (Ant Colony)
- `cache/` – Caching infrastructure (multi-strategy invalidation)
- `cerebrum/` – Case-based reasoning and Bayesian inference
- `ci_cd_automation/` – CI/CD pipelines (includes build automation, formerly `build_synthesis`)
- `cli/` – Command line interface
- `cloud/` – Cloud provider integration (includes cost management)
- `coding/` – Code execution, review, static analysis, pattern matching (includes formerly standalone `static_analysis/`, `pattern_matching/`, `tree_sitter/`)
- `collaboration/` – Team collaboration and multi-agent sessions
- `compression/` – Data compression
- `concurrency/` – Concurrency utilities, distributed sync, rate limiting
- `config_management/` – Configuration management
- `containerization/` – Container management (Docker/K8s)
- `crypto/` – Cryptographic operations
- `dark/` – Dark mode and PDF processing
- `data_visualization/` – Charts, plots, and visualization (includes formerly standalone `visualization/`)
- `database_management/` – Database operations, migrations, backups, lineage
- `defense/` – Active fiduciary defense
- `dependency_injection/` – IoC container and lifecycle
- `deployment/` – Deployment automation (blue-green, canary, rolling)
- `documentation/` – Documentation generation (includes education content)
- `documents/` – Document processing and RAG chunking
- `edge_computing/` – Edge deployment and IoT scenarios
- `embodiment/` – Physical/robotic integration
- `encryption/` – Data encryption and digital signing
- `environment_setup/` – Environment validation and setup
- `events/` – Event system, pub/sub, streaming, notifications
- `evolutionary_ai/` – Evolutionary algorithms
- `examples/` – Usage examples
- `exceptions/` – Centralized exception hierarchy
- `feature_flags/` – Feature flag management
- `finance/` – Financial ledger and treasury
- `fpf/` – Functional Programming Framework
- `git_operations/` – Git automation and merge resolution
- `graph_rag/` – Graph-based RAG
- `ide/` – IDE integration
- `identity/` – Identity and Persona Management
- `llm/` – LLM infrastructure (includes inference optimization, multimodal)
- `logging_monitoring/` – Centralized logging
- `logistics/` – Workflow logistics and orchestration
- `maintenance/` – Dependency analysis and project maintenance
- `market/` – Anonymous marketplaces
- `meme/` – Unified Memetic Warfare & Information Dynamics
- `model_context_protocol/` – MCP interfaces and auto-discovery
- `model_ops/` – ML model operations (includes evaluation, registry, feature store, optimization)
- `module_template/` – Module scaffolding
- `networking/` – Network utilities (includes service mesh)
- `orchestrator/` – Workflow orchestration (includes scheduling)
- `performance/` – Performance monitoring and profiling
- `physical_management/` – Physical systems
- `plugin_system/` – Plugin architecture
- `privacy/` – Data minimization and mixnets
- `prompt_engineering/` – Prompt design, optimization, and testing
- `quantum/` – Quantum computing simulation
- `relations/` – CRM and Social Graph (includes UOR)
- `scrape/` – Web scraping
- `search/` – Search and indexing
- `security/` – Security scanning (includes governance)
- `serialization/` – Data serialization
- `skills/` – Agent skills library
- `spatial/` – 3D/4D modeling
- `system_discovery/` – Module discovery
- `telemetry/` – Telemetry, tracing, metrics, dashboards
- `templating/` – Template management
- `terminal_interface/` – Terminal UI
- `testing/` – Test utilities (includes chaos engineering, workflow testing)
- `tests/` – Test suites (unit and integration)
- `tool_use/` – LLM tool usage
- `utils/` – General utilities (includes i18n, hashing, retry)
- `validation/` – Input validation (includes schemas)
- `vector_store/` – Vector database abstraction
- `video/` – Video processing
- `wallet/` – Self-custody wallets (includes smart contracts)
- `website/` – Website generation (includes accessibility)

## Operating Contracts

- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.

## Signposting

### Document Hierarchy

- **Self**: [AGENTS.md](AGENTS.md) — Module coordination hub
- **Parent**: [src/AGENTS.md](../AGENTS.md) — Source directory coordination

### Sibling Documents

- [README.md](README.md) — Package overview
- [SPEC.md](SPEC.md) — Technical specification
- [PAI.md](PAI.md) — Personal AI Infrastructure

### Navigation Links

- **📁 Parent Directory**: [src](../README.md)
- **🏠 Project Root**: [../../README.md](../../README.md)
