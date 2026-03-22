# Codomyrmex Agents — Repository Root

**Version**: v1.2.7 | **Status**: Active | **Last Updated**: March 2026

## Purpose

This is the root coordination document for all AI agents operating within the Codomyrmex repository. It defines the top-level structure, surfaces, and operating contracts that govern agent interactions across the entire project.

Codomyrmex is a modular coding workspace enabling AI development workflows with **128** top-level modules under `src/codomyrmex/`. This document serves as the central navigation hub for agents working with any part of the system. Repo metrics: [docs/reference/inventory.md](docs/reference/inventory.md).

## Repository Structure

### Primary Surfaces

The repository is organized into distinct surfaces, each with specific responsibilities:

| Surface | Purpose | Documentation |
| :--- | :--- | :--- |
| **src/** | Core source modules implementing functionality | [src/README.md](src/README.md) |
| **scripts/** | Maintenance and automation utilities | [scripts/README.md](scripts/README.md) |
| **docs/** | Project documentation (about Codomyrmex) | [docs/README.md](docs/README.md) |
| **src/codomyrmex/tests/** | Test suites (unit and integration) | [src/codomyrmex/tests/README.md](src/codomyrmex/tests/README.md) |
| **config/** | Configuration templates and examples | [config/README.md](config/README.md) |
| **projects/** | Project workspace and templates | [projects/README.md](projects/README.md) |
| **src/codomyrmex/examples/** | Executable examples and demos | [src/codomyrmex/examples/README.md](src/codomyrmex/examples/README.md) |
| **scripts/sair/** | SAIR Mathematics Distillation submodule | [scripts/sair/README.md](scripts/sair/README.md) |

## Key Files

- `README.md` - Primary entry point for users and contributors
- `AGENTS.md` - This file: agent coordination and navigation
- `LICENSE` - MIT License
- `SECURITY.md` - Security policies and vulnerability reporting
- `pyproject.toml` - Python package configuration
- `pytest.ini` - Test configuration
- `Makefile` - Build and automation tasks
- `uv.lock` - Python dependency lock file
- `start_here.sh` - Interactive entry point for exploration
- `package.json` - Node.js package configuration

## Dependencies

- All dependencies are managed via `uv` (for Python) and `npm`/`yarn` (for JS/TS).
- See `pyproject.toml` and `package.json` for explicit version constraints.
- No direct dependencies between modular layers are permitted without interface contracts.

## Development Guidelines

- **Zero-Mock Policy:** All tests must use real components. No mocks.
- **Coverage Gate:** Ensure test coverage exceeds 35.0% on new features.
- **Documentation:** Maintain `AGENTS.md`, `README.md`, and `SPEC.md` parity on structural changes.

## Operating Contracts

### Universal Agent Protocols

All agents operating within this repository must:

1. **Respect Modularity**: Each module is self-contained. Changes within one module should minimize impact on others.

2. **Maintain Documentation Alignment**: Code, documentation, and workflows must remain synchronized. When updating code, update corresponding documentation.

3. **Follow Coding Standards**: Adhere to coding standards defined in project documentation and `.editorconfig`.

4. **Use Structured Logging**: All operations must use the centralized logging system (`src/codomyrmex/logging_monitoring/`).

5. **Preserve Model Context Protocol Interfaces**: MCP tool specifications must remain available and functional for sibling agents.

6. **Record Telemetry**: Outcomes and metrics should be recorded in shared telemetry systems.

7. **Update Task Queues**: Maintain task items for pending work and cross-agent coordination.

### Surface-Specific Guidelines

#### src/ - Source Code

- Follow Python best practices (PEP 8)
- Maintain test coverage (≥33%)
- Update `API_SPECIFICATION.md` when changing interfaces
- Document MCP tools in `MCP_TOOL_SPECIFICATION.md`
- Version changes in `CHANGELOG.md`

#### scripts/ - Automation

- Scripts should be idempotent where possible
- Include usage documentation in script headers
- Log all significant operations
- Handle errors gracefully with informative messages

#### docs/ - Documentation

- Documentation is about Codomyrmex (not tools Codomyrmex provides)
- Use clear, understated language ("show not tell")
- Maintain navigation links between related documents
- Keep examples current with codebase

#### src/codomyrmex/tests/ - Tests

- Follow test-driven development (TDD) practices
- Use real data analysis (no mock methods)
- Organize by test type (unit, integration)
- Include performance benchmarks where applicable

## Module Discovery

### Core Functional Modules

Located in `src/codomyrmex/`, these modules provide the primary capabilities:

**Foundation Layer**:

- `logging_monitoring/` - Centralized logging system
  - Key Classes: `Logger`, `LogAggregator`, `StructuredLogger`
  - Key Functions: `get_logger(name: str) -> Logger`, `setup_logging(config: dict) -> None`
- `environment_setup/` - Environment validation and setup
  - Key Classes: `EnvironmentValidator`, `DependencyChecker`, `ConfigLoader`
  - Key Functions: `validate_environment() -> bool`, `check_dependencies(requirements: list) -> dict`
- `model_context_protocol/` - AI communication standards
  - Key Classes: `MCPClient`, `ToolSpecification`, `ModelInterface`
  - Key Functions: `register_tool(name: str, spec: dict) -> bool`, `call_tool(name: str, params: dict) -> Any`
- `terminal_interface/` - Rich terminal interactions
  - Key Classes: `TerminalUI`, `ProgressBar`, `InteractivePrompt`
  - Key Functions: `display_table(data: list, headers: list) -> None`, `confirm_action(message: str) -> bool`

**Core Layer**:

- `agents/` - Agentic framework integrations
  - Key Classes: `AgentInterface`, `BaseAgent`, `JulesClient`, `ClaudeClient`, `CodexClient`, `HermesClient`, `AgentOrchestrator`
  - Key Functions: `execute(request: AgentRequest) -> AgentResponse`
  - Key Submodules: `ai_code_editing/`, `droid/` (task management), `claude/`, `codex/`, `hermes/` (dual-backend: CLI + Ollama, session persistence, prompt templates)
- `static_analysis/` - Code quality analysis
  - Key Classes: `CodeAnalyzer`, `LintRunner`, `ComplexityCalculator`
  - Key Functions: `analyze_file(filepath: str) -> dict`, `calculate_complexity(code: str) -> float`
- `coding/` - Code interaction and sandboxing
  - Key Submodules: `sandbox/`, `review/`, `execution/`
  - Key Classes: `SandboxExecutor`, `CodeReviewer`, `ExecutionContext`
  - Key Functions: `execute_code(code: str, language: str) -> ExecutionResult`, `review_code(code: str) -> dict`
- `data_visualization/` - Charts and plots
  - Key Classes: `PlotGenerator`, `ChartBuilder`, `DataProcessor`
  - Key Functions: `create_plot(data: pd.DataFrame, plot_type: str) -> str`, `save_visualization(fig: Any, filepath: str) -> None`
- `search/` - Code search and retrieval
  - Key Classes: `SearchEngine`, `IndexBuilder`, `CodeSearcher`
  - Key Functions: `search(query: str, corpus: list) -> list`, `build_index(path: str) -> Index`
- `git_operations/` - Version control automation
  - Key Classes: `GitManager`, `CommitBuilder`, `BranchManager`
  - Key Functions: `commit_changes(message: str, files: list = None) -> str`, `create_branch(name: str) -> bool`
- `security/` - Security scanning and threat assessment
  - Key Submodules: `cognitive/`, `digital/`, `physical/`, `theory/`
  - Key Classes: `SecurityScanner`, `VulnerabilityDetector`, `ComplianceChecker`, `ThreatModeler`
  - Key Functions: `scan_codebase(path: str) -> dict`, `check_vulnerabilities(dependencies: dict) -> list`, `assess_threats(system: dict) -> ThreatAssessment`
- `llm/` - LLM infrastructure and integration
  - Key Submodules: `ollama/`, `outputs/`, `prompt_templates/`
  - Key Classes: `OllamaClient`, `ModelManager`, `InferenceEngine`
  - Key Functions: `load_model(name: str) -> bool`, `generate_text(prompt: str, model: str) -> str`
- `performance/` - Performance monitoring
  - Key Classes: `PerformanceProfiler`, `BenchmarkRunner`, `MetricsCollector`
  - Key Functions: `profile_function(func: callable, *args, **kwargs) -> ProfileResult`, `run_benchmark(test_func: callable) -> dict`

**Service Layer**:

- `deployment/` - Deployment automation
  - Key Classes: `DeploymentManager`, `RollbackHandler`
  - Key Functions: `deploy(config: dict) -> DeployResult`, `rollback(deployment_id: str) -> bool`
- `documentation/` - Documentation generation tools
  - Key Classes: `DocGenerator`, `APIDocumenter`, `MarkdownRenderer`
  - Key Functions: `generate_docs(source_path: str, output_path: str) -> None`, `extract_api_docs(code: str) -> dict`
- `api/` - API infrastructure
  - Key Submodules: `documentation/`, `standardization/`
  - Key Classes: `OpenAPISpecGenerator`, `APIVersioner`, `RESTAPIBuilder`
  - Key Functions: `generate_openapi_spec(routes: list) -> dict`, `version_api(api: dict) -> dict`
- `ci_cd_automation/` - CI/CD pipeline management
  - Key Classes: `PipelineBuilder`, `DeploymentManager`, `TestRunner`
  - Key Functions: `create_pipeline(config: dict) -> Pipeline`, `deploy_to_environment(app: str, env: str) -> bool`
- `containerization/` - Container management
  - Key Classes: `DockerManager`, `ContainerOrchestrator`, `ImageBuilder`
  - Key Functions: `build_image(dockerfile: str, tag: str) -> str`, `deploy_container(config: dict) -> bool`
- `database_management/` - Database operations
  - Key Classes: `DatabaseClient`, `SchemaManager`, `MigrationRunner`
  - Key Functions: `execute_query(query: str, params: dict = None) -> list`, `run_migration(migration_file: str) -> bool`
- `orchestrator/` - Workflow orchestration
  - Key Classes: `WorkflowEngine`, `TaskScheduler`, `DependencyGraph`
  - Key Functions: `execute_workflow(workflow_id: str, context: dict) -> WorkflowResult`
- `config_management/` - Configuration management
  - Key Classes: `ConfigManager`, `SecretHandler`, `EnvironmentLoader`
  - Key Functions: `load_config(path: str) -> dict`, `get_secret(key: str) -> str`

**Specialized Layer**:

- `spatial/` - Spatial modeling (3D/4D)
  - Key Submodules: `three_d/`, `four_d/`, `world_models/`
  - Key Classes: `SceneBuilder`, `MeshGenerator`, `Renderer`
  - Key Functions: `create_scene(objects: list) -> Scene`, `render_scene(scene: Scene) -> Image`
- `physical_management/` - Physical system simulation
  - Key Classes: `SystemMonitor`, `ResourceManager`, `PerformanceTracker`
  - Key Functions: `get_system_info() -> dict`, `monitor_resources(interval: int) -> Iterator[dict]`
- `system_discovery/` - System exploration and module discovery
  - Key Classes: `ModuleScanner`, `CapabilityDetector`, `HealthChecker`
  - Key Functions: `discover_modules() -> list`, `check_module_health(module_name: str) -> HealthStatus`
- `cerebrum/` - Case-based reasoning and Bayesian inference
  - Key Classes: `CerebrumEngine`, `CaseBase`, `BayesianNetwork`, `ActiveInferenceAgent`
  - Key Functions: `reason(case: Case, context: dict) -> ReasoningResult`, `infer(network: BayesianNetwork, evidence: dict) -> InferenceResult`
- `fpf/` - Feed-Parse-Format Pipeline
  - Key Classes: `FPFOrchestrator`, `CombinatorEngine`, `TransformationPipeline`
  - Key Functions: `compose(functions: list) -> ComposedFunction`, `transform(data: Any, pipeline: Pipeline) -> Any`
- `documents/` - Document processing and management
  - Key Classes: `DocumentProcessor`, `MetadataExtractor`, `SearchEngine`, `Transformer`
  - Key Functions: `process_document(path: str) -> Document`, `search(query: str, corpus: list) -> list`
- `events/` - Event system and pub/sub
  - Key Classes: `EventBus`, `EventEmitter`, `EventHandler`
  - Key Functions: `emit(event: Event) -> None`, `subscribe(event_type: str, handler: callable) -> None`
- `plugin_system/` - Plugin architecture and management
  - Key Classes: `PluginManager`, `PluginLoader`, `PluginRegistry`
  - Key Functions: `load_plugin(path: str) -> Plugin`, `register_plugin(plugin: Plugin) -> None`
- `tool_use/` - Tool invocation and management
  - Key Classes: `ToolRegistry`, `ToolExecutor`
  - Key Functions: `register_tool(name: str, tool: callable) -> None`, `execute_tool(name: str, args: dict) -> Any`
- `utils/` - General utilities
  - Key Functions: `ensure_directory`, `safe_write`
- `validation/` - Input validation
  - Key Classes: `Validator`, `Schema`
- `templating/` - Template management
  - Key Classes: `TemplateEngine`
- `ide/` - IDE Integration
  - Key Classes: `EditorInterface`
- `cloud/` - Cloud provider integration
  - Key Classes: `AWSClient`, `GCPClient`, `InfomaniakComputeClient`
- `networking/` - Network utilities
  - Key Classes: `NetworkClient`, `HTTPClient`
- `serialization/` - Data serialization
  - Key Classes: `Serializer`
- `compression/` - Data compression
  - Key Classes: `Compressor`
- `encryption/` - Data encryption
  - Key Classes: `Encrypter`
- `scrape/` - Web scraping
  - Key Classes: `Scraper`
- `auth/` - Authentication and authorization
  - Key Classes: `AuthManager`, `TokenHandler`
- `cache/` - Caching infrastructure
  - Key Classes: `CacheManager`, `CacheStrategy`
- `collaboration/` - Team collaboration tools
  - Key Classes: `CollaborationSession`, `SyncManager`
- `concurrency/` - Concurrency utilities
  - Key Classes: `AsyncExecutor`, `TaskPool`
- `embodiment/` - Physical embodiment interfaces
  - Key Classes: `EmbodimentInterface`, `SensorManager`
- `evolutionary_ai/` - Evolutionary AI algorithms
  - Key Classes: `EvolutionaryOptimizer`, `GeneticAlgorithm`
- `feature_flags/` - Feature flag management
  - Key Classes: `FeatureFlagManager`, `FlagEvaluator`
- `model_ops/` - ML model operations
  - Key Classes: `ModelManager`, `ModelRegistry`
- `skills/` - Agent skills and capabilities
  - Key Classes: `SkillRegistry`, `SkillExecutor`
- `telemetry/` - Telemetry and observability
  - Key Classes: `TelemetryClient`, `TraceManager`
- `website/` - Website generation and management
  - Key Classes: `WebsiteBuilder`, `PageGenerator`
- `meme/` - Memetics & Information Dynamics *(Experimental — not yet MCP-exposed)*
  - Key Classes: `MemeSpecific`, `NarrativeEngine`
- `agentic_memory/` - Long-term agent memory, recall, and Obsidian vault integration
  - Key Classes: `AgentMemory`, `VectorStoreMemory`
  - Key Submodule: `obsidian/` — 19-module dual-mode Obsidian integration (filesystem + CLI)
  - Key Functions: `ObsidianVault(path)`, `search_vault()`, `create_note()`, `build_link_graph()`, `parse_canvas()`
- `audio/` - Audio processing, transcription, and streaming
  - Key Classes: `AudioProcessor`, `Transcriber`
  - Key Submodule: `streaming/` — WebSocket streaming pipeline with `AudioStreamServer`, `AudioStreamClient`, `CodecNegotiator`, energy-based `VAD`
- `vision/` - Local-first visual understanding (VLM via Ollama)
  - Key Classes: `VLMClient`, `PDFExtractor`, `AnnotationExtractor`
  - Key Functions: `analyze_image(path) -> VLMResponse`, `extract_text(pdf_path) -> str`
- `bio_simulation/` - Biological simulation
  - Key Classes: `BioSimulator`
- `crypto/` - Cryptographic utilities
  - Key Classes: `CryptoEngine`
- `dark/` - Dark mode utilities for PDFs and interfaces
  - Key Classes: `DarkModeConverter`
- `dependency_injection/` - Dependency injection framework
  - Key Classes: `Container`, `Provider`
- `edge_computing/` - Edge computing and IoT
  - Key Classes: `EdgeNode`, `EdgeOrchestrator`
- `finance/` - Financial operations and tracking
  - Key Classes: `FinanceTracker`, `TransactionManager`
- `formal_verification/` - Formal verification and proofs
  - Key Classes: `Verifier`, `ProofEngine`
- `graph_rag/` - Graph-based retrieval augmented generation
  - Key Classes: `GraphRAG`, `KnowledgeGraph`
- `logistics/` - Logistics-layer orchestration and scheduling
  - Key Classes: `LogisticsPlanner`, `ShipmentTracker`
- `maintenance/` - Documentation maintenance utilities
  - Key Functions: `update_root_docs`, `finalize_docs`
- `networks/` - Network topology and analysis
  - Key Classes: `NetworkAnalyzer`, `TopologyBuilder`

- `prompt_engineering/` - Prompt engineering and optimization
  - Key Classes: `PromptOptimizer`, `PromptTemplate`
- `quantum/` - Quantum computing interfaces
  - Key Classes: `QuantumCircuit`, `QuantumSimulator`
- `relations/` - Relationship management
  - Key Classes: `RelationshipManager`
- `simulation/` - Simulation framework
  - Key Classes: `Simulator`, `SimulationEngine`
- `vector_store/` - Vector storage and similarity search
  - Key Classes: `InMemoryVectorStore`, `VectorIndex`
- `video/` - Video processing and analysis *(Stub — exceptions only, not yet implemented)*
  - Key Classes: `VideoProcessor`, `FrameExtractor`

**Secure Cognitive Layer** *(Experimental — modules exist but are not yet MCP-exposed via the PAI bridge)*:

- `identity/` - Multi-persona and bio-verification
  - Key Classes: `IdentityManager`, `BioCognitiveVerifier`, `Persona`
- `wallet/` - Self-custody and recovery
  - Key Classes: `WalletManager`, `NaturalRitualRecovery`
- `defense/` - Active defense and rabbit holes
  - Key Classes: `ActiveDefense`, `RabbitHole`
- `market/` - Anonymous marketplaces
  - Key Classes: `ReverseAuction`, `DemandAggregator`
- `privacy/` - Data minimization and mixnets
  - Key Classes: `CrumbCleaner`, `MixnetProxy`

**Development Layer**:

- `module_template/` - Module creation templates and scaffolding
  - Key Classes: `ModuleGenerator`, `TemplateRenderer`, `ScaffoldBuilder`
  - Key Functions: `create_module(name: str, template: str) -> bool`, `generate_scaffold(config: dict) -> dict`

See [docs/modules/overview.md](docs/modules/overview.md) for module documentation.

## Navigation

### For Users

- **Start Here**: [README.md](README.md) - Project overview and quick start
- **Getting Started**: [docs/getting-started/quickstart.md](docs/getting-started/quickstart.md)
- **Architecture**: [docs/project/architecture.md](docs/project/architecture.md)
- **Contributing**: [docs/project/contributing.md](docs/project/contributing.md)

### For Agents

- **Coding Standards**: [.editorconfig](.editorconfig)
- **Module System**: [docs/modules/overview.md](docs/modules/overview.md)
- **Module Relationships**: [docs/modules/relationships.md](docs/modules/relationships.md)
- **API Reference**: [docs/reference/api.md](docs/reference/api.md)

## Signposting

### Document Hierarchy

- **Self**: [AGENTS.md](AGENTS.md) - This document (root agent coordination)
- **Parent**: [README.md](README.md) - Project overview and entry point

### Sibling Documents (Root Level)

- [README.md](README.md) - Project overview and quick start
- [SPEC.md](SPEC.md) - Functional specification
- [PAI.md](PAI.md) - Personal AI Infrastructure documentation
- [SECURITY.md](SECURITY.md) - Security policies

### Child AGENTS.md Files

| Directory | AGENTS.md | Purpose |
| :--- | :--- | :--- |
| **src/** | [src/AGENTS.md](src/AGENTS.md) | Source code coordination |
| **src/codomyrmex/** | [src/codomyrmex/AGENTS.md](src/codomyrmex/AGENTS.md) | Module coordination hub |
| **docs/** | [docs/AGENTS.md](docs/AGENTS.md) | Documentation coordination |
| **scripts/** | [scripts/AGENTS.md](scripts/AGENTS.md) | Automation scripts coordination |
| **config/** | [config/AGENTS.md](config/AGENTS.md) | Configuration coordination |
| **projects/** | [projects/AGENTS.md](projects/AGENTS.md) | Project workspace coordination |

### Key Module AGENTS.md Files

| Module | AGENTS.md | Layer |
| :--- | :--- | :--- |
| **logging_monitoring** | [src/codomyrmex/logging_monitoring/AGENTS.md](src/codomyrmex/logging_monitoring/AGENTS.md) | Foundation |
| **environment_setup** | [src/codomyrmex/environment_setup/AGENTS.md](src/codomyrmex/environment_setup/AGENTS.md) | Foundation |
| **model_context_protocol** | [src/codomyrmex/model_context_protocol/AGENTS.md](src/codomyrmex/model_context_protocol/AGENTS.md) | Foundation |
| **terminal_interface** | [src/codomyrmex/terminal_interface/AGENTS.md](src/codomyrmex/terminal_interface/AGENTS.md) | Foundation |
| **agents** | [src/codomyrmex/agents/AGENTS.md](src/codomyrmex/agents/AGENTS.md) | Core |
| **static_analysis** | [src/codomyrmex/static_analysis/AGENTS.md](src/codomyrmex/static_analysis/AGENTS.md) | Core |
| **coding** | [src/codomyrmex/coding/AGENTS.md](src/codomyrmex/coding/AGENTS.md) | Core |
| **llm** | [src/codomyrmex/llm/AGENTS.md](src/codomyrmex/llm/AGENTS.md) | Core |
| **cerebrum** | [src/codomyrmex/cerebrum/AGENTS.md](src/codomyrmex/cerebrum/AGENTS.md) | Specialized |
| **meme** | [src/codomyrmex/meme/AGENTS.md](src/codomyrmex/meme/AGENTS.md) | Specialized |
| **orchestrator** | [src/codomyrmex/orchestrator/AGENTS.md](src/codomyrmex/orchestrator/AGENTS.md) | Service |

### For Contributors

- **Development Setup**: [docs/development/environment-setup.md](docs/development/environment-setup.md)
- **Testing Strategy**: [docs/development/testing-strategy.md](docs/development/testing-strategy.md)
- **Documentation Guide**: [docs/development/documentation.md](docs/development/documentation.md)

## Agent Coordination

### Cross-Module Operations

When an operation spans multiple modules:

1. **Check Dependencies**: Review `docs/modules/relationships.md` for dependency graph
2. **Coordinate Logging**: Use consistent log levels and structured data
3. **Share Context**: Use MCP tools to pass context between agents
4. **Update Documentation**: Ensure all affected modules' docs are updated

### Conflict Resolution

If conflicting guidance is found:

1. **Hierarchy**: Specific overrides general (module rules > general rules)
2. **Rationale**: Conflicts should state explicit rationale
3. **Escalation**: Document unresolved conflicts in task items

### Quality Gates

Before completing significant changes:

1. **Tests Pass**: All relevant tests must pass
2. **Linting Clean**: No new linting errors
3. **Documentation Updated**: Changes reflected in docs
4. **AGENTS.md Current**: Module AGENTS.md reflects changes
5. **Links Valid**: All documentation links functional
6. **Measured, Not Assumed**: Claims about performance, coverage, or behaviour are backed by recent measurements or tests rather than guesses.

## Version History

- **v1.2.3** (March 2026) — Codebase Health, API Freeze, Config Validation, Typed Events, Performance Profiling
- **v1.1.8** (March 2026) — Persistent memory, Obsidian sync, multi-hop Graph RAG, active inference
- **v1.1.7** (March 2026) — Repository-wide documentation audit and consistency sweep
- **v1.1.6** (March 2026) — Hermes dual-backend, Gemini package migration
- **v1.1.5** (March 2026) — Type safety diagnostics, coverage gate ratcheted to 35%
- **v1.1.4** (March 2026) — Ruff zero, 128 modules, 595 `@mcp_tool` decorators, RASP doc compliance 128/128
- **v1.1.0** (March 2026) — Production readiness, zero-mock hardening
- **v1.0.7** (March 2026) — MCP expansion: 74 auto-discovered modules, ~367 tools
- **v0.1.0** (February 2026) — Initial repository structure and agent coordination framework

## Related Documentation

- **[Architecture](docs/project/architecture.md)** - System architecture and design principles
- **[Contributing](docs/project/contributing.md)** - Contributing guidelines and workflow

<!-- gitnexus:start -->
# GitNexus — Code Intelligence

This project is indexed by GitNexus as **codomyrmex** (90294 symbols, 206389 relationships, 300 execution flows). Use the GitNexus MCP tools to understand code, assess impact, and navigate safely.

> If any GitNexus tool warns the index is stale, run `npx gitnexus analyze` in terminal first.

## Always Do

- **MUST run impact analysis before editing any symbol.** Before modifying a function, class, or method, run `gitnexus_impact({target: "symbolName", direction: "upstream"})` and report the blast radius (direct callers, affected processes, risk level) to the user.
- **MUST run `gitnexus_detect_changes()` before committing** to verify your changes only affect expected symbols and execution flows.
- **MUST warn the user** if impact analysis returns HIGH or CRITICAL risk before proceeding with edits.
- When exploring unfamiliar code, use `gitnexus_query({query: "concept"})` to find execution flows instead of grepping. It returns process-grouped results ranked by relevance.
- When you need full context on a specific symbol — callers, callees, which execution flows it participates in — use `gitnexus_context({name: "symbolName"})`.

## When Debugging

1. `gitnexus_query({query: "<error or symptom>"})` — find execution flows related to the issue
2. `gitnexus_context({name: "<suspect function>"})` — see all callers, callees, and process participation
3. `READ gitnexus://repo/codomyrmex/process/{processName}` — trace the full execution flow step by step
4. For regressions: `gitnexus_detect_changes({scope: "compare", base_ref: "main"})` — see what your branch changed

## When Refactoring

- **Renaming**: MUST use `gitnexus_rename({symbol_name: "old", new_name: "new", dry_run: true})` first. Review the preview — graph edits are safe, text_search edits need manual review. Then run with `dry_run: false`.
- **Extracting/Splitting**: MUST run `gitnexus_context({name: "target"})` to see all incoming/outgoing refs, then `gitnexus_impact({target: "target", direction: "upstream"})` to find all external callers before moving code.
- After any refactor: run `gitnexus_detect_changes({scope: "all"})` to verify only expected files changed.

## Never Do

- NEVER edit a function, class, or method without first running `gitnexus_impact` on it.
- NEVER ignore HIGH or CRITICAL risk warnings from impact analysis.
- NEVER rename symbols with find-and-replace — use `gitnexus_rename` which understands the call graph.
- NEVER commit changes without running `gitnexus_detect_changes()` to check affected scope.

## Tools Quick Reference

| Tool | When to use | Command |
|------|-------------|---------|
| `query` | Find code by concept | `gitnexus_query({query: "auth validation"})` |
| `context` | 360-degree view of one symbol | `gitnexus_context({name: "validateUser"})` |
| `impact` | Blast radius before editing | `gitnexus_impact({target: "X", direction: "upstream"})` |
| `detect_changes` | Pre-commit scope check | `gitnexus_detect_changes({scope: "staged"})` |
| `rename` | Safe multi-file rename | `gitnexus_rename({symbol_name: "old", new_name: "new", dry_run: true})` |
| `cypher` | Custom graph queries | `gitnexus_cypher({query: "MATCH ..."})` |

## Impact Risk Levels

| Depth | Meaning | Action |
|-------|---------|--------|
| d=1 | WILL BREAK — direct callers/importers | MUST update these |
| d=2 | LIKELY AFFECTED — indirect deps | Should test |
| d=3 | MAY NEED TESTING — transitive | Test if critical path |

## Resources

| Resource | Use for |
|----------|---------|
| `gitnexus://repo/codomyrmex/context` | Codebase overview, check index freshness |
| `gitnexus://repo/codomyrmex/clusters` | All functional areas |
| `gitnexus://repo/codomyrmex/processes` | All execution flows |
| `gitnexus://repo/codomyrmex/process/{name}` | Step-by-step execution trace |

## Self-Check Before Finishing

Before completing any code modification task, verify:
1. `gitnexus_impact` was run for all modified symbols
2. No HIGH/CRITICAL risk warnings were ignored
3. `gitnexus_detect_changes()` confirms changes match expected scope
4. All d=1 (WILL BREAK) dependents were updated

## Keeping the Index Fresh

After committing code changes, the GitNexus index becomes stale. Re-run analyze to update it:

```bash
npx gitnexus analyze
```

If the index previously included embeddings, preserve them by adding `--embeddings`:

```bash
npx gitnexus analyze --embeddings
```

To check whether embeddings exist, inspect `.gitnexus/meta.json` — the `stats.embeddings` field shows the count (0 means no embeddings). **Running analyze without `--embeddings` will delete any previously generated embeddings.**

> Claude Code users: A PostToolUse hook handles this automatically after `git commit` and `git merge`.

## CLI

| Task | Read this skill file |
|------|---------------------|
| Understand architecture / "How does X work?" | `.claude/skills/gitnexus/gitnexus-exploring/SKILL.md` |
| Blast radius / "What breaks if I change X?" | `.claude/skills/gitnexus/gitnexus-impact-analysis/SKILL.md` |
| Trace bugs / "Why is X failing?" | `.claude/skills/gitnexus/gitnexus-debugging/SKILL.md` |
| Rename / extract / split / refactor | `.claude/skills/gitnexus/gitnexus-refactoring/SKILL.md` |
| Tools, resources, schema reference | `.claude/skills/gitnexus/gitnexus-guide/SKILL.md` |
| Index, status, clean, wiki CLI commands | `.claude/skills/gitnexus/gitnexus-cli/SKILL.md` |

<!-- gitnexus:end -->

## qmd Skill

This project is configured with the `qmd` skill for local hybrid search of Markdown notes and docs.

| Task | Read this skill file |
| --- | --- |
| Search notes, docs, or knowledge base | `.claude/skills/qmd/SKILL.md` |
