# Codomyrmex Module Documentation Index

**Version**: v1.1.4 | **Status**: Active | **Last Updated**: March 2026

## Overview

This directory contains the extended documentation for all codomyrmex modules. Each module subdirectory has three documentation files:

- **readme.md** -- Comprehensive module overview, architecture, key classes, usage examples, and configuration
- **AGENTS.md** -- Agent integration guide with MCP tool reference tables and trust classifications
- **SPEC.md** -- Technical specification with functional requirements, interface contracts, and non-functional requirements

## Module Inventory

### Foundation Layer

Modules that provide core infrastructure used by all other layers.

| Module | MCP Tools | Description |
|--------|-----------|-------------|
| [environment_setup](environment_setup/readme.md) | 2 | Environment validation and dependency checking |
| [exceptions](exceptions/readme.md) | 0 | Centralized exception hierarchy |
| [logging_monitoring](logging_monitoring/readme.md) | 1 | Structured logging and monitoring integration |
| [model_context_protocol](model_context_protocol/readme.md) | 3 | MCP server inspection and tool registry |
| [terminal_interface](terminal_interface/readme.md) | 3 | Rich terminal output and formatting |
| [utils](utils/readme.md) | 3 | Shared utility functions |

### Core Layer

Primary capabilities that power the platform.

| Module | MCP Tools | Description |
|--------|-----------|-------------|
| [agents](agents/readme.md) | 3 | Multi-provider AI agent framework (13 providers) |
| [agentic_memory](agentic_memory/readme.md) | 3 | Agent memory store, retrieve, and semantic search |
| [auth](auth/readme.md) | 3 | Authentication, token management, and RBAC |
| [cache](cache/readme.md) | 4 | Multi-backend caching (in-memory, Redis, disk) |
| [cerebrum](cerebrum/readme.md) | 2 | Case-based reasoning and active inference |
| [coding](coding/readme.md) | 5 | Code execution sandbox, review, and debugging |
| [collaboration](collaboration/readme.md) | 3 | Multi-agent swarm coordination |
| [compression](compression/readme.md) | 0 | gzip/zlib/ZIP/Zstandard compression |
| [concurrency](concurrency/readme.md) | 2 | Thread/process pools and lock management |
| [config_management](config_management/readme.md) | 3 | Configuration get/set/validate |
| [crypto](crypto/readme.md) | 3 | Hashing, key generation, and verification |
| [encryption](encryption/readme.md) | 2 | Symmetric and asymmetric encryption |
| [events](events/readme.md) | 3 | Event bus with emit, history, and type registry |
| [git_operations](git_operations/readme.md) | 35 | Full git automation (35 MCP tools) |
| [llm](llm/readme.md) | 4 | LLM infrastructure (Ollama, providers, Fabric) |
| [networking](networking/readme.md) | 0 | HTTP clients and network utilities |
| [search](search/readme.md) | 3 | Full-text, fuzzy, and indexed search |
| [serialization](serialization/readme.md) | 3 | JSON/YAML/MessagePack serialization |
| [static_analysis](static_analysis/readme.md) | 3 | Code quality, linting, and security scanning |
| [validation](validation/readme.md) | 3 | Schema validation and config validation |

### Service Layer

Higher-level orchestration and domain services.

| Module | MCP Tools | Description |
|--------|-----------|-------------|
| [api](api/readme.md) | 3 | REST/GraphQL API framework with rate limiting |
| [calendar_integration](calendar_integration/readme.md) | 5 | Calendar event management and scheduling |
| [ci_cd_automation](ci_cd_automation/readme.md) | 3 | Pipeline management and build automation |
| [cli](cli/readme.md) | 2 | Command-line interface entry point |
| [cloud](cloud/readme.md) | 3 | AWS/GCS/Azure/Coda/Infomaniak cloud services |
| [containerization](containerization/readme.md) | 4 | Docker build, scan, and runtime management |
| [data_visualization](data_visualization/readme.md) | 2 | Chart/dashboard generation and HTML export |
| [database_management](database_management/readme.md) | 3 | Database connection and migration management |
| [deployment](deployment/readme.md) | 3 | Deployment orchestration and rollback |
| [documentation](docs_gen/readme.md) | 2 | Documentation generation and RASP auditing |
| [email](email/readme.md) | 12 | AgentMail and Gmail integration (12 MCP tools) |
| [feature_flags](feature_flags/readme.md) | 3 | Feature flag management with strategies |
| [formal_verification](formal_verification/readme.md) | 8 | Z3 constraint solving and model checking |
| [git_analysis](git_analysis/readme.md) | 16 | Git history analysis and contributor stats |
| [ide](ide/readme.md) | 2 | IDE integration and Antigravity engine |
| [maintenance](maintenance/readme.md) | 2 | Health checks and task management |
| [model_ops](model_ops/readme.md) | 3 | ML model operations and feature store |
| [orchestrator](orchestrator/readme.md) | 2 | Workflow execution and scheduling |
| [performance](performance/readme.md) | 2 | Benchmarking and regression detection |
| [plugin_system](plugin_system/readme.md) | 2 | Plugin discovery and dependency resolution |
| [prompt_engineering](prompt_engineering/readme.md) | 4 | Prompt template management |
| [scrape](scrape/readme.md) | 2 | HTML content extraction and text similarity |
| [security](security/readme.md) | 3 | Vulnerability scanning and secret detection |
| [skills](skills/readme.md) | 7 | Skill discovery, listing, and invocation |
| [system_discovery](system_discovery/readme.md) | 3 | Module discovery and health monitoring |
| [testing](testing/readme.md) | 2 | Test runner and framework utilities |
| [tool_use](tool_use/readme.md) | 2 | Tool execution and registration |
| [tree_sitter](tree_sitter/readme.md) | 3 | AST parsing and code structure analysis |
| [vector_store](vector_store/readme.md) | 4 | Vector embedding storage and similarity search |

### Application Layer

User-facing interfaces and specialized domains.

| Module | MCP Tools | Description |
|--------|-----------|-------------|
| [audio](audio/readme.md) | 2 | Speech-to-text and text-to-speech |
| [bio_simulation](bio_simulation/readme.md) | 0 | Biological simulation (ant colony, genetics) |
| [dark](dark/readme.md) | 0 | Dark pattern detection and analysis |
| [defense](defense/readme.md) | 0 | Defensive security measures |
| [documents](documents/readme.md) | 3 | Document transformation and processing |
| [edge_computing](edge_computing/readme.md) | 0 | Edge deployment and management |
| [embodiment](embodiment/readme.md) | 0 | Physical agent embodiment |
| [evolutionary_ai](evolutionary_ai/readme.md) | 0 | Evolutionary algorithms and genetic programming |
| [finance](finance/readme.md) | 0 | Financial analysis utilities |
| [fpf](fpf/readme.md) | 0 | Fetch-Parse-Format pipeline |
| [graph_rag](graph_rag/readme.md) | 0 | Graph-based retrieval-augmented generation |
| [identity](identity/readme.md) | 0 | Digital identity management |
| [logistics](logistics/readme.md) | 0 | Logistics orchestration |
| [market](market/readme.md) | 0 | Market analysis |
| [meme](meme/readme.md) | 0 | Meme generation |
| [networks](networks/readme.md) | 0 | Network topology and analysis |
| [operating_system](operating_system/readme.md) | 6 | OS-level operations (Linux/Mac/Windows) |
| [physical_management](physical_management/readme.md) | 0 | Physical device management |
| [privacy](privacy/readme.md) | 0 | Privacy compliance utilities |
| [quantum](quantum/readme.md) | 0 | Quantum computing interfaces |
| [relations](relations/readme.md) | 1 | Relationship strength scoring |
| [release](release/readme.md) | 0 | Release management workflows |
| [simulation](simulation/readme.md) | 0 | General simulation framework |
| [spatial](spatial/readme.md) | 0 | 3D spatial and geospatial operations |
| [telemetry](telemetry/readme.md) | 0 | Telemetry collection and SLO tracking |
| [video](video/readme.md) | 0 | Video processing and generation |
| [wallet](wallet/readme.md) | 0 | Cryptocurrency wallet management |
| [website](website/readme.md) | 0 | Web server and accessibility testing |

### Support

| Module | MCP Tools | Description |
|--------|-----------|-------------|
| [dependency_injection](dependency_injection/readme.md) | 0 | DI container and service registration |
| [examples](examples/readme.md) | 0 | Example code and tutorials |
| [module_template](module_template/readme.md) | 0 | Template for creating new modules |
| [tests](tests/readme.md) | 0 | Cross-module test infrastructure |

## Statistics

- **Total modules**: 87 documented
- **MCP-enabled modules**: 55 (with at least 1 MCP tool)
- **Total MCP tools**: ~235 auto-discovered via `@mcp_tool` decorator
- **Documentation pattern**: RASP (README, AGENTS, SPEC, PAI)

## Navigation

- **Source modules**: [src/codomyrmex/](../../../src/codomyrmex/)
- **PAI integration**: [PAI.md](../../../PAI.md)
- **Project root**: [CLAUDE.md](../../../CLAUDE.md)
