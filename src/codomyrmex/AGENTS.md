# Codomyrmex Agents — src/codomyrmex

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose

This is the module coordination hub for all Codomyrmex source modules. It contains 50+ modules organized in a layered architecture (Foundation → Core → Service → Specialized) with no circular dependencies.

## Active Components

### Foundation Layer (No Dependencies)

| Module | Purpose | Key Classes/Functions |
| :--- | :--- | :--- |
| `logging_monitoring/` | Centralized logging | `setup_logging()`, `get_logger()`, `JSONFormatter` |
| `environment_setup/` | Environment validation | `EnvironmentValidator`, `DependencyChecker` |
| `model_context_protocol/` | MCP standards | `MCPClient`, `ToolSpecification` |
| `terminal_interface/` | Terminal UI | `TerminalUI`, `ProgressBar`, `confirm_action()` |
| `config_management/` | Configuration | `ConfigManager`, `SecretHandler` |
| `metrics/` | Metrics collection | `MetricsCollector` |

### Core Layer (Depends on Foundation)

| Module | Purpose | Key Classes/Functions |
| :--- | :--- | :--- |
| `agents/` | AI agent integrations | `AgentOrchestrator`, `ClaudeClient`, `CodeEditor` |
| `static_analysis/` | Code analysis | `CodeAnalyzer`, `LintRunner` |
| `coding/` | Code execution | `SandboxExecutor`, `CodeReviewer` |
| `data_visualization/` | Visualization | `PlotGenerator`, `ChartBuilder` |
| `pattern_matching/` | Pattern recognition | `PatternMatcher`, `ASTAnalyzer` |
| `git_operations/` | Git automation | `GitManager`, `CommitBuilder` |
| `security/` | Security scanning | `SecurityScanner`, `VulnerabilityDetector` |
| `llm/` | LLM infrastructure | `OllamaManager`, `ModelRunner`, `FabricManager` |
| `performance/` | Performance profiling | `PerformanceProfiler`, `BenchmarkRunner` |

### Service Layer (Depends on Foundation + Core)

| Module | Purpose | Key Classes/Functions |
| :--- | :--- | :--- |
| `build_synthesis/` | Build automation | `BuildOrchestrator`, `ArtifactBuilder` |
| `documentation/` | Doc generation | `DocGenerator`, `APIDocumenter` |
| `api/` | API infrastructure | `OpenAPISpecGenerator`, `RESTAPIBuilder` |
| `ci_cd_automation/` | CI/CD pipelines | `PipelineBuilder`, `DeploymentManager` |
| `containerization/` | Containers | `DockerManager`, `ImageBuilder` |
| `database_management/` | Database ops | `DatabaseClient`, `MigrationRunner` |
| `orchestrator/` | Workflow orchestration | `WorkflowEngine`, `TaskScheduler` |
| `logistics/` | Task management | `LogisticsManager` |
| `auth/` | Authentication | `AuthManager` |
| `cloud/` | Cloud integrations | `AWSClient`, `GCPClient` |

### Specialized Layer (Full Stack)

| Module | Purpose | Key Classes/Functions |
| :--- | :--- | :--- |
| `cerebrum/` | Reasoning engine | `CerebrumEngine`, `BayesianNetwork`, `ActiveInferenceAgent` |
| `fpf/` | Functional programming | `FPFOrchestrator`, `CombinatorEngine` |
| `spatial/` | 3D/4D modeling | `SceneBuilder`, `MeshGenerator` |
| `events/` | Event system | `EventBus`, `EventEmitter` |
| `plugin_system/` | Plugin architecture | `PluginManager`, `PluginLoader` |
| `skills/` | Skills management | `SkillsManager` |
| `ide/` | IDE integration | `EditorInterface` |
| `documents/` | Document processing | `DocumentProcessor`, `SearchEngine` |
| `system_discovery/` | System exploration | `ModuleScanner`, `CapabilityDetector` |
| `module_template/` | Module scaffolding | `ModuleGenerator`, `TemplateRenderer` |

### Utility Modules

| Module | Purpose |
| :--- | :--- |
| `utils/` | Common utilities |
| `validation/` | Input validation |
| `serialization/` | Data serialization |
| `compression/` | Data compression |
| `encryption/` | Cryptographic ops |
| `networking/` | Network utilities |
| `scrape/` | Web scraping |
| `templating/` | Template engine |
| `cache/` | Caching backends |
| `website/` | Website generation |
| `cli/` | CLI utilities |
| `tests/` | Test suites |
| `examples/` | Example code |

## Operating Contracts

1. **Layer Dependencies**: Higher layers may only depend on lower layers
2. **Logging**: All modules use `logging_monitoring` for structured logging
3. **Configuration**: Modules use `config_management` for settings
4. **MCP Tools**: Modules expose MCP-compatible tool specifications
5. **Documentation**: Each module maintains README.md, AGENTS.md, and SPEC.md
6. **Testing**: Modules maintain ≥80% test coverage

## Signposting

### Document Hierarchy

- **Self**: [AGENTS.md](AGENTS.md)
- **Parent**: [src/AGENTS.md](../AGENTS.md)
- **Project Root**: [../../AGENTS.md](../../AGENTS.md)

### Child Module AGENTS.md Files

#### Foundation Layer
- [logging_monitoring/AGENTS.md](logging_monitoring/AGENTS.md)
- [environment_setup/AGENTS.md](environment_setup/AGENTS.md)
- [model_context_protocol/AGENTS.md](model_context_protocol/AGENTS.md)
- [terminal_interface/AGENTS.md](terminal_interface/AGENTS.md)

#### Core Layer
- [agents/AGENTS.md](agents/AGENTS.md)
- [static_analysis/AGENTS.md](static_analysis/AGENTS.md)
- [coding/AGENTS.md](coding/AGENTS.md)
- [llm/AGENTS.md](llm/AGENTS.md)
- [git_operations/AGENTS.md](git_operations/AGENTS.md)

#### Service Layer
- [build_synthesis/AGENTS.md](build_synthesis/AGENTS.md)
- [documentation/AGENTS.md](documentation/AGENTS.md)
- [api/AGENTS.md](api/AGENTS.md)
- [orchestrator/AGENTS.md](orchestrator/AGENTS.md)

#### Specialized Layer
- [cerebrum/AGENTS.md](cerebrum/AGENTS.md)
- [fpf/AGENTS.md](fpf/AGENTS.md)
- [spatial/AGENTS.md](spatial/AGENTS.md)
- [events/AGENTS.md](events/AGENTS.md)

### Related Documentation

- [README.md](README.md) - Module overview
- [SPEC.md](SPEC.md) - Functional specification
- [PAI.md](PAI.md) - Personal AI Infrastructure (local)
- [Root PAI.md](../../PAI.md) - Project PAI documentation
- [Module System Docs](../../docs/modules/overview.md) - Module system documentation
