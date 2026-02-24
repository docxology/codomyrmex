# Codomyrmex Agents — Repository Root

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Purpose

This is the root coordination document for all AI agents operating within the Codomyrmex repository. It defines the top-level structure, surfaces, and operating contracts that govern agent interactions across the entire project.

Codomyrmex is a modular coding workspace enabling AI development workflows with 78 specialized modules. This document serves as the central navigation hub for agents working with any part of the system.

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
| **cursorrules/** | Coding standards and automation rules | [cursorrules/README.md](cursorrules/README.md) |
| **projects/** | Project workspace and templates | [projects/README.md](projects/README.md) |
| **src/codomyrmex/examples/** | Executable examples and demos | [src/codomyrmex/examples/README.md](src/codomyrmex/examples/README.md) |

### Repository Root Files

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
- `cursorrules/general.cursorrules` - General coding standards (in `cursorrules/` directory)
- `resources.json` - Resource configuration
- `test.db` - Generated test database (artifact, not source)
- `workflow.db` - Generated workflow database (artifact, not source)

## Operating Contracts

### Universal Agent Protocols

All agents operating within this repository must:

1. **Respect Modularity**: Each module is self-contained. Changes within one module should minimize impact on others.

2. **Maintain Documentation Alignment**: Code, documentation, and workflows must remain synchronized. When updating code, update corresponding documentation.

3. **Follow Cursorrules**: Adhere to coding standards defined in `cursorrules/general.cursorrules` and module-specific rules.

4. **Use Structured Logging**: All operations must use the centralized logging system (`src/codomyrmex/logging_monitoring/`).

5. **Preserve Model Context Protocol Interfaces**: MCP tool specifications must remain available and functional for sibling agents.

6. **Record Telemetry**: Outcomes and metrics should be recorded in shared telemetry systems.

7. **Update Task Queues**: Maintain task items for pending work and cross-agent coordination.

### Surface-Specific Guidelines

#### src/ - Source Code

- Follow Python best practices (PEP 8)
- Maintain test coverage (≥80%)
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
  - Key Classes: `AgentInterface`, `BaseAgent`, `JulesClient`, `ClaudeClient`, `CodexClient`, `AgentOrchestrator`
  - Key Functions: `execute(request: AgentRequest) -> AgentResponse`
  - Key Submodules: `ai_code_editing/`, `droid/` (task management), `claude/`, `codex/`
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
- `fpf/` - Functional Programming Framework
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
- `tools/` - Utility tools and helpers
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
- `deployment/` - Deployment automation
  - Key Classes: `DeploymentManager`, `RollbackHandler`
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
- `meme/` - Memetics & Information Dynamics
  - Key Classes: `MemeSpecific`, `NarrativeEngine`
- `agentic_memory/` - Long-term agent memory and recall
  - Key Classes: `AgentMemory`, `VectorStoreMemory`
- `audio/` - Audio processing and transcription
  - Key Classes: `AudioProcessor`, `Transcriber`
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
- `search/` - Search and retrieval
  - Key Classes: `SearchEngine`, `IndexBuilder`
- `simulation/` - Simulation framework
  - Key Classes: `Simulator`, `SimulationEngine`
- `tool_use/` - Tool invocation and management
  - Key Classes: `ToolRegistry`, `ToolExecutor`
- `vector_store/` - Vector storage and similarity search
  - Key Classes: `InMemoryVectorStore`, `VectorIndex`
- `video/` - Video processing and analysis
  - Key Classes: `VideoProcessor`, `FrameExtractor`

**Secure Cognitive Layer**:

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

- **Coding Standards**: [cursorrules/general.cursorrules](cursorrules/general.cursorrules)
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
| **cursorrules/** | [cursorrules/AGENTS.md](cursorrules/AGENTS.md) | Coding standards coordination |
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

## Active Components

- `package.json` – Node.js package configuration
- `projects/` – Project workspace and templates
- `pyproject.toml` – Python package configuration
- `pytest.ini` – Test configuration
- `resources.json` – Resource configuration
- `scripts/` – Maintenance and automation utilities
- `src/` – Core source modules implementing functionality
- `start_here.sh` – Interactive entry point for exploration
- `test.db` – Test database file
- `src/codomyrmex/tests/` – Test suites (unit and integration)
- `workflow.db` – Workflow database file
- `output/` – Generated reports and documentation artifacts

## Navigation Links

- **Main Documentation**: [README.md](README.md) - Main project README
- **Documentation Hub**: [docs/README.md](docs/README.md) - Documentation structure
- **Source Code**: [src/README.md](src/README.md) - Source code structure
- **Scripts**: [scripts/README.md](scripts/README.md) - Scripts directory
- **Testing**: [src/codomyrmex/tests/README.md](src/codomyrmex/tests/README.md) - Testing suite
- **Configuration**: [config/README.md](config/README.md) - Configuration templates
- **Cursor Rules**: [cursorrules/README.md](cursorrules/README.md) - Coding standards
- **Projects**: [projects/README.md](projects/README.md) - Projects workspace
- **Examples**: [src/codomyrmex/examples/README.md](src/codomyrmex/examples/README.md) - Executable examples and demos

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

## Version History

- **v0.1.7** (February 2026) - Module count corrected to 82, version synchronized, missing modules added to discovery
- **v0.1.6** (February 2026) - Agent & memory foundations, event orchestration
- **v0.1.0** (February 2026) - Initial repository structure and agent coordination framework

## Related Documentation

- **[Module Overview](docs/modules/overview.md)** - Module system documentation
- **[Architecture](docs/project/architecture.md)** - System architecture and design principles
- **[Cursorrules](cursorrules/README.md)** - Detailed coding standards and automation rules
- **[Contributing](docs/project/contributing.md)** - Contributing guidelines and workflow

<!-- gitnexus:start -->
# GitNexus MCP

This project is indexed by GitNexus as **codomyrmex** (40099 symbols, 103186 relationships, 300 execution flows).

GitNexus provides a knowledge graph over this codebase — call chains, blast radius, execution flows, and semantic search.

## Always Start Here

For any task involving code understanding, debugging, impact analysis, or refactoring, you must:

1. **Read `gitnexus://repo/{name}/context`** — codebase overview + check index freshness
2. **Match your task to a skill below** and **read that skill file**
3. **Follow the skill's workflow and checklist**

> If step 1 warns the index is stale, run `npx gitnexus analyze` in the terminal first.

## Skills

| Task | Read this skill file |
|------|---------------------|
| Understand architecture / "How does X work?" | `.claude/skills/gitnexus/exploring/SKILL.md` |
| Blast radius / "What breaks if I change X?" | `.claude/skills/gitnexus/impact-analysis/SKILL.md` |
| Trace bugs / "Why is X failing?" | `.claude/skills/gitnexus/debugging/SKILL.md` |
| Rename / extract / split / refactor | `.claude/skills/gitnexus/refactoring/SKILL.md` |

## Tools Reference

| Tool | What it gives you |
|------|-------------------|
| `query` | Process-grouped code intelligence — execution flows related to a concept |
| `context` | 360-degree symbol view — categorized refs, processes it participates in |
| `impact` | Symbol blast radius — what breaks at depth 1/2/3 with confidence |
| `detect_changes` | Git-diff impact — what do your current changes affect |
| `rename` | Multi-file coordinated rename with confidence-tagged edits |
| `cypher` | Raw graph queries (read `gitnexus://repo/{name}/schema` first) |
| `list_repos` | Discover indexed repos |

## Resources Reference

Lightweight reads (~100-500 tokens) for navigation:

| Resource | Content |
|----------|---------|
| `gitnexus://repo/{name}/context` | Stats, staleness check |
| `gitnexus://repo/{name}/clusters` | All functional areas with cohesion scores |
| `gitnexus://repo/{name}/cluster/{clusterName}` | Area members |
| `gitnexus://repo/{name}/processes` | All execution flows |
| `gitnexus://repo/{name}/process/{processName}` | Step-by-step trace |
| `gitnexus://repo/{name}/schema` | Graph schema for Cypher |

## Graph Schema

**Nodes:** File, Function, Class, Interface, Method, Community, Process
**Edges (via CodeRelation.type):** CALLS, IMPORTS, EXTENDS, IMPLEMENTS, DEFINES, MEMBER_OF, STEP_IN_PROCESS

```cypher
MATCH (caller)-[:CodeRelation {type: 'CALLS'}]->(f:Function {name: "myFunc"})
RETURN caller.name, caller.filePath
```

<!-- gitnexus:end -->
