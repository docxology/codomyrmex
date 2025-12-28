# Codomyrmex Agents — Repository Root

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: December 2025

## Purpose

This is the root coordination document for all AI agents operating within the Codomyrmex repository. It defines the top-level structure, surfaces, and operating contracts that govern agent interactions across the entire project.

Codomyrmex is a modular coding workspace enabling AI development workflows. This document serves as the central navigation hub for agents working with any part of the system.

## Repository Structure

### Primary Surfaces

The repository is organized into distinct surfaces, each with specific responsibilities:

| Surface | Purpose | Documentation |
|---------|---------|---------------|
| **src/** | Core source modules implementing functionality | [src/README.md](src/README.md) |
| **scripts/** | Maintenance and automation utilities | [scripts/README.md](scripts/README.md) |
| **docs/** | Project documentation (about Codomyrmex) | [docs/README.md](docs/README.md) |
| **testing/** | Test suites (unit and integration) | [testing/README.md](testing/README.md) |
| **config/** | Configuration templates and examples | [config/README.md](config/README.md) |
| **cursorrules/** | Coding standards and automation rules | [cursorrules/README.md](cursorrules/README.md) |
| **projects/** | Project workspace and templates | [projects/README.md](projects/README.md) |
| **examples/** | Example scripts and demonstrations | [examples/README.md](examples/README.md) |
| **scripts/examples/** | Executable examples and demos | [scripts/examples/README.md](scripts/examples/README.md) |

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
- `uv.lock` - Python dependency lock file
- `general.cursorrules` - General coding standards
- `resources.json` - Resource configuration
- `test.db` - Test database file
- `workflow.db` - Workflow database file

## Operating Contracts

### Universal Agent Protocols

All agents operating within this repository must:

1. **Respect Modularity**: Each module is self-contained. Changes within one module should minimize impact on others.

2. **Maintain Documentation Alignment**: Code, documentation, and workflows must remain synchronized. When updating code, update corresponding documentation.

3. **Follow Cursorrules**: Adhere to coding standards defined in `cursorrules/general.cursorrules` and module-specific rules.

4. **Use Structured Logging**: All operations must use the centralized logging system (`src/codomyrmex/logging_monitoring/`).

5. **Preserve Model Context Protocol Interfaces**: MCP tool specifications must remain available and functional for sibling agents.

6. **Record Telemetry**: Outcomes and metrics should be recorded in shared telemetry systems.

7. **Update TODO Queues**: Maintain TODO items for pending work and cross-agent coordination.

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

#### testing/ - Tests
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
- `ai_code_editing/` - AI-powered code assistance
  - Key Classes: `AICodeEditor`, `CodeGenerator`, `RefactoringEngine`
  - Key Functions: `generate_code(prompt: str, language: str) -> str`, `refactor_code(code: str, instructions: str) -> str`
- `static_analysis/` - Code quality analysis
  - Key Classes: `CodeAnalyzer`, `LintRunner`, `ComplexityCalculator`
  - Key Functions: `analyze_file(filepath: str) -> dict`, `calculate_complexity(code: str) -> float`
- `code_execution_sandbox/` - Safe code execution
  - Key Classes: `SandboxExecutor`, `ResourceLimiter`, `ExecutionContext`
  - Key Functions: `execute_code(code: str, language: str, timeout: int = 30) -> ExecutionResult`
- `data_visualization/` - Charts and plots
  - Key Classes: `PlotGenerator`, `ChartBuilder`, `DataProcessor`
  - Key Functions: `create_plot(data: pd.DataFrame, plot_type: str) -> str`, `save_visualization(fig: Any, filepath: str) -> None`
- `pattern_matching/` - Code pattern analysis
  - Key Classes: `PatternMatcher`, `ASTAnalyzer`, `CodePattern`
  - Key Functions: `find_patterns(code: str, patterns: list) -> list`, `extract_dependencies(filepath: str) -> dict`
- `git_operations/` - Version control automation
  - Key Classes: `GitManager`, `CommitBuilder`, `BranchManager`
  - Key Functions: `commit_changes(message: str, files: list = None) -> str`, `create_branch(name: str) -> bool`
- `code_review/` - Automated code review
  - Key Classes: `CodeReviewer`, `ReviewEngine`, `CommentGenerator`
  - Key Functions: `review_pull_request(pr_number: int, repo: str) -> ReviewResult`, `analyze_code_quality(code: str) -> dict`
- `security_audit/` - Security scanning
  - Key Classes: `SecurityScanner`, `VulnerabilityDetector`, `ComplianceChecker`
  - Key Functions: `scan_codebase(path: str) -> list`, `check_vulnerabilities(dependencies: dict) -> list`
- `ollama_integration/` - Local LLM integration
  - Key Classes: `OllamaClient`, `ModelManager`, `InferenceEngine`
  - Key Functions: `load_model(name: str) -> bool`, `generate_text(prompt: str, model: str) -> str`
- `language_models/` - LLM infrastructure
  - Key Classes: `ModelProvider`, `TokenCounter`, `EmbeddingGenerator`
  - Key Functions: `get_completion(messages: list, model: str) -> str`, `calculate_tokens(text: str) -> int`
- `performance/` - Performance monitoring
  - Key Classes: `PerformanceProfiler`, `BenchmarkRunner`, `MetricsCollector`
  - Key Functions: `profile_function(func: callable, *args, **kwargs) -> ProfileResult`, `run_benchmark(test_func: callable) -> dict`

**Service Layer**:
- `build_synthesis/` - Build automation
  - Key Classes: `BuildOrchestrator`, `ArtifactBuilder`, `DependencyResolver`
  - Key Functions: `build_project(config: dict) -> BuildResult`, `resolve_dependencies(requirements: list) -> dict`
- `documentation/` - Documentation generation tools
  - Key Classes: `DocGenerator`, `APIDocumenter`, `MarkdownRenderer`
  - Key Functions: `generate_docs(source_path: str, output_path: str) -> None`, `extract_api_docs(code: str) -> dict`
- `api_documentation/` - API documentation generation
  - Key Classes: `OpenAPISpecGenerator`, `SwaggerRenderer`, `EndpointAnalyzer`
  - Key Functions: `generate_openapi_spec(routes: list) -> dict`, `create_swagger_ui(spec: dict) -> str`
- `ci_cd_automation/` - CI/CD pipeline management
  - Key Classes: `PipelineBuilder`, `DeploymentManager`, `TestRunner`
  - Key Functions: `create_pipeline(config: dict) -> Pipeline`, `deploy_to_environment(app: str, env: str) -> bool`
- `containerization/` - Container management
  - Key Classes: `DockerManager`, `ContainerOrchestrator`, `ImageBuilder`
  - Key Functions: `build_image(dockerfile: str, tag: str) -> str`, `deploy_container(config: dict) -> bool`
- `database_management/` - Database operations
  - Key Classes: `DatabaseClient`, `SchemaManager`, `MigrationRunner`
  - Key Functions: `execute_query(query: str, params: dict = None) -> list`, `run_migration(migration_file: str) -> bool`
- `project_orchestration/` - Workflow orchestration
  - Key Classes: `WorkflowEngine`, `TaskScheduler`, `DependencyGraph`
  - Key Functions: `execute_workflow(workflow_id: str, context: dict) -> WorkflowResult`
- `config_management/` - Configuration management
  - Key Classes: `ConfigManager`, `SecretHandler`, `EnvironmentLoader`
  - Key Functions: `load_config(path: str) -> dict`, `get_secret(key: str) -> str`

**Specialized Layer**:
- `modeling_3d/` - 3D modeling and visualization
  - Key Classes: `SceneBuilder`, `MeshGenerator`, `Renderer`
  - Key Functions: `create_scene(objects: list) -> Scene`, `render_scene(scene: Scene, camera: Camera) -> Image`
- `physical_management/` - Physical system simulation
  - Key Classes: `SystemMonitor`, `ResourceManager`, `PerformanceTracker`
  - Key Functions: `get_system_info() -> dict`, `monitor_resources(interval: int) -> Iterator[dict]`
- `system_discovery/` - System exploration and module discovery
  - Key Classes: `ModuleScanner`, `CapabilityDetector`, `HealthChecker`
  - Key Functions: `discover_modules() -> list`, `check_module_health(module_name: str) -> HealthStatus`

**Development Layer**:
- `module_template/` - Module creation templates and scaffolding
  - Key Classes: `ModuleGenerator`, `TemplateRenderer`, `ScaffoldBuilder`
  - Key Functions: `create_module(name: str, template: str) -> bool`, `generate_scaffold(config: dict) -> dict`
- `template/` - Code generation templates
  - Key Classes: `TemplateEngine`, `CodeTemplate`, `SnippetGenerator`
  - Key Functions: `render_template(template_name: str, context: dict) -> str`

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

### For Contributors
- **Development Setup**: [docs/development/environment-setup.md](docs/development/environment-setup.md)
- **Testing Strategy**: [docs/development/testing-strategy.md](docs/development/testing-strategy.md)
- **Documentation Guide**: [docs/development/documentation.md](docs/development/documentation.md)

## Active Components
- `@output/` – Committed reports and documentation artifacts
- `AGENTS.md` – This file: agent coordination and navigation
- `LICENSE` – MIT License
- `Makefile` – Build and automation tasks
- `README.md` – Primary entry point for users and contributors
- `SECURITY.md` – Security policies and vulnerability reporting
- `.editorconfig` – Editor configuration standards
- `.pre-commit-config.yaml` – Pre-commit hook configuration
- `config/` – Configuration templates and examples
- `cursorrules/` – Coding standards and automation rules
- `docs/` – Project documentation (about Codomyrmex)
- `examples/` – Example scripts and demonstrations
- `general.cursorrules` – General coding standards
- `output/` – Runtime-generated outputs and working files
- `package.json` – Node.js package configuration
- `projects/` – Project workspace and templates
- `pyproject.toml` – Python package configuration
- `pytest.ini` – Test configuration
- `resources.json` – Resource configuration
- `scripts/` – Maintenance and automation utilities
- `src/` – Core source modules implementing functionality
- `start_here.sh` – Interactive entry point for exploration
- `test.db` – Test database file
- `testing/` – Test suites (unit and integration)
- `uv.lock` – Python dependency lock file
- `workflow.db` – Workflow database file

## Navigation Links
- **Main Documentation**: [README.md](README.md) - Main project README
- **Documentation Hub**: [docs/README.md](docs/README.md) - Documentation structure
- **Source Code**: [src/README.md](src/README.md) - Source code structure
- **Scripts**: [scripts/README.md](scripts/README.md) - Scripts directory
- **Testing**: [testing/README.md](testing/README.md) - Testing suite
- **Configuration**: [config/README.md](config/README.md) - Configuration templates
- **Cursor Rules**: [cursorrules/README.md](cursorrules/README.md) - Coding standards
- **Projects**: [projects/README.md](projects/README.md) - Projects workspace
- **Examples**: [examples/README.md](examples/README.md) - Example implementations
- **Scripts Examples**: [scripts/examples/README.md](scripts/examples/README.md) - Executable examples and demos
- **Source Agents**: [src/AGENTS.md](src/AGENTS.md) - Source code agent coordination
- **Docs Agents**: [docs/AGENTS.md](docs/AGENTS.md) - Documentation agent coordination
- **Scripts Agents**: [scripts/AGENTS.md](scripts/AGENTS.md) - Scripts agent coordination
- **Testing Agents**: [testing/AGENTS.md](testing/AGENTS.md) - Testing agent coordination
- **Config Agents**: [config/AGENTS.md](config/AGENTS.md) - Configuration agents
- **Rules Agents**: [cursorrules/AGENTS.md](cursorrules/AGENTS.md) - Cursor rules agents
- **Projects Agents**: [projects/AGENTS.md](projects/AGENTS.md) - Projects agent coordination

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
3. **Escalation**: Document unresolved conflicts in TODO items

### Quality Gates

Before completing significant changes:

1. **Tests Pass**: All relevant tests must pass
2. **Linting Clean**: No new linting errors
3. **Documentation Updated**: Changes reflected in docs
4. **AGENTS.md Current**: Module AGENTS.md reflects changes
5. **Links Valid**: All documentation links functional

## Version History

- **v0.1.0** (December 2025) - Initial repository structure and agent coordination framework

## Related Documentation

- **[Module Overview](docs/modules/overview.md)** - Module system documentation
- **[Architecture](docs/project/architecture.md)** - System architecture and design principles
- **[Cursorrules](cursorrules/README.md)** - Detailed coding standards and automation rules
- **[Contributing](docs/project/contributing.md)** - Contributing guidelines and workflow
