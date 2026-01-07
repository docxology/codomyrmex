# Codomyrmex Agents — src/codomyrmex/build_synthesis

## Signposting
- **Parent**: [codomyrmex](../AGENTS.md)
- **Self**: [Agents](AGENTS.md)
- **Children**:
    - [docs](docs/AGENTS.md)
    - [tests](tests/AGENTS.md)
- **Key Artifacts**:
    - [Functional Spec](SPEC.md)
    - [Human Readme](README.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose
Build automation, dependency management, artifact synthesis, and deployment orchestration. Takes raw source code, configuration, and assets, and transforms them into deployable artifacts (Python packages, Docker images, static sites). Abstracts complexities of different build systems (pip, docker, npm) behind a unified Pythonic interface with support for cross-language builds and parallel execution.

## Active Components
- `API_SPECIFICATION.md` – Detailed API specification
- `CHANGELOG.md` – Version history
- `MCP_TOOL_SPECIFICATION.md` – MCP tool specification
- `README.md` – Project file
- `SECURITY.md` – Security considerations
- `SPEC.md` – Project file
- `USAGE_EXAMPLES.md` – Usage examples
- `__init__.py` – Module exports and public API
- `build_manager.py` – Build management and target definitions
- `build_orchestrator.py` – Build orchestration and pipeline execution
- `docs/` – Directory containing docs components
- `requirements.txt` – Project file
- `tests/` – Directory containing tests components

## Key Classes and Functions

### BuildManager (`build_manager.py`)
- `BuildManager()` – Main build management class
- `create_build_target(name: str, build_type: BuildType, config: dict) -> BuildTarget` – Create a build target
- `trigger_build(target: str, config: dict = None, output_path_suggestion: str = None, clean_build: bool = False, build_options: dict = None) -> dict` – Trigger a build
- `get_available_build_types() -> list[BuildType]` – Get available build types
- `get_available_environments() -> list[BuildEnvironment]` – Get available build environments

### BuildTarget (`build_manager.py`)
- `BuildTarget` (base class) – Build target definition:
  - `name: str` – Target name
  - `build_type: BuildType` – Type of build
  - `steps: list[BuildStep]` – Build steps
  - `dependencies: list[Dependency]` – Build dependencies
- `create_python_build_target(name: str, config: dict) -> BuildTarget` – Create Python build target
- `create_docker_build_target(name: str, config: dict) -> BuildTarget` – Create Docker build target
- `create_static_build_target(name: str, config: dict) -> BuildTarget` – Create static site build target

### BuildOrchestrator (`build_orchestrator.py`)
- `check_build_environment() -> dict` – Check build environment setup
- `run_build_command(command: str, cwd: str = None) -> dict` – Execute build commands
- `synthesize_build_artifact(artifact_type: str, config: dict) -> dict` – Create build artifacts
- `validate_build_output(output_path: str, expected_format: str) -> bool` – Validate build outputs
- `orchestrate_build_pipeline(target: BuildTarget, config: dict = None) -> BuildResult` – Orchestrate complete build pipelines

### BuildResult (`build_manager.py`)
- `BuildResult` (dataclass) – Result of a build operation:
  - `status: BuildStatus` – Build status
  - `artifact_paths: list[str]` – Paths to build artifacts
  - `logs: str` – Build logs
  - `metadata: dict[str, Any]` – Build metadata

### BuildStatus (`build_manager.py`)
- `BuildStatus` (Enum) – Build status states: PENDING, RUNNING, SUCCESS, FAILED, CANCELLED

### BuildType (`build_manager.py`)
- `BuildType` (Enum) – Types of builds supported: PYTHON, DOCKER, STATIC, CUSTOM

### BuildEnvironment (`build_manager.py`)
- `BuildEnvironment` (Enum) – Build environments: DEVELOPMENT, STAGING, PRODUCTION

### Dependency (`build_manager.py`)
- `Dependency` (dataclass) – Dependency definition:
  - `name: str` – Dependency name
  - `type: DependencyType` – Dependency type
  - `version: Optional[str]` – Version requirement
  - `check_command: Optional[str]` – Command to check dependency availability

## Operating Contracts
- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.

## Navigation Links
- **Human Documentation**: [README.md](README.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **📁 Parent Directory**: [codomyrmex](../README.md) - Parent directory documentation
- **🏠 Project Root**: [README](../../../README.md) - Main project documentation