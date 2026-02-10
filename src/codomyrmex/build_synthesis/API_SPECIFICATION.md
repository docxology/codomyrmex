# Build Synthesis - API Specification

## Introduction

The Build Synthesis module provides functionalities for automating build processes, dependency management, artifact synthesis, and deployment orchestration within the Codomyrmex project. This document outlines the direct Python API functions and data structures available for build management.

For details on the MCP tools, please refer to the [MCP Tool Specification](./MCP_TOOL_SPECIFICATION.md).

## Core Python API Functions

### Build Management

1.  **`trigger_build(target_name: str = None, environment: str = "development", config_path: str = None) -> bool`**
    *   **Description**: Trigger a build process for the specified target or all targets. Initializes a `BuildManager`, converts the environment string to a `BuildEnvironment` enum, and executes the build.
    *   **Arguments**:
        *   `target_name` (str, optional): Name of the build target to execute. If `None`, builds all targets.
        *   `environment` (str, optional): Build environment name (`"development"`, `"production"`, `"staging"`, `"testing"`). Default: `"development"`.
        *   `config_path` (str, optional): Path to build configuration file (YAML or JSON). Default: `None` (uses `build.yaml` in project root).
    *   **Returns** (bool): `True` if the build succeeded, `False` otherwise.

2.  **`check_build_environment() -> dict`**
    *   **Description**: Check if the build environment is properly configured by probing for common build tools (`make`, `cmake`, `ninja`, `gcc`, `python3`).
    *   **Returns** (dict):
        ```python
        {
            "python_available": bool,
            "make_available": bool,
            "cmake_available": bool,
            "ninja_available": bool,
            "gcc_available": bool,
            "available_tools": list[str],
            "all_required_available": bool
        }
        ```

3.  **`run_build_command(command: list[str], cwd: str = None) -> tuple[bool, str, str]`**
    *   **Description**: Run a build command and return the result. Executes the command with a 5-minute timeout.
    *   **Arguments**:
        *   `command` (list[str]): List of command arguments.
        *   `cwd` (str, optional): Working directory for the command. Default: `None`.
    *   **Returns** (tuple[bool, str, str]): Tuple of `(success, stdout, stderr)`.

4.  **`synthesize_build_artifact(source_path: str, output_path: str, artifact_type: str = "executable") -> bool`**
    *   **Description**: Synthesize a build artifact from source code. Supports `"executable"` (Python wrapper scripts) and `"package"` (directory copy) artifact types.
    *   **Arguments**:
        *   `source_path` (str): Path to source file or directory.
        *   `output_path` (str): Path where artifact should be created.
        *   `artifact_type` (str, optional): Type of artifact to create (`"executable"`, `"library"`, `"package"`). Default: `"executable"`.
    *   **Returns** (bool): `True` if synthesis was successful, `False` otherwise.

5.  **`validate_build_output(output_path: str) -> dict[str, Any]`**
    *   **Description**: Validate that build output meets expectations. Checks file existence, executability, size, and basic content validity.
    *   **Arguments**:
        *   `output_path` (str): Path to the build output.
    *   **Returns** (dict):
        ```python
        {
            "exists": bool,
            "is_file": bool,
            "is_executable": bool,
            "size_bytes": int,
            "errors": list[str]
        }
        ```

6.  **`orchestrate_build_pipeline(build_config: dict[str, Any]) -> dict[str, Any]`**
    *   **Description**: Orchestrate a complete build pipeline with stages: environment check, dependency installation, build execution, artifact synthesis, and output validation.
    *   **Arguments**:
        *   `build_config` (dict): Dictionary containing build configuration with optional keys: `"dependencies"` (list[str]), `"build_commands"` (list[list[str]]), `"working_directory"` (str), `"artifacts"` (list of dicts with `"source"`, `"output"`, `"type"`).
    *   **Returns** (dict):
        ```python
        {
            "stages": [{"name": str, "success": bool, ...}],
            "overall_success": bool,
            "artifacts": [{"source": str, "output": str, "success": bool}],
            "errors": list[str]
        }
        ```

### Build Target Convenience Functions

7.  **`create_python_build_target(name: str, source_path: str, output_path: str = None, dependencies: list[str] = None) -> BuildTarget`**
    *   **Description**: Create a Python build target with predefined steps (install dependencies, run tests, build package, create distribution).
    *   **Arguments**:
        *   `name` (str): Target name.
        *   `source_path` (str): Path to source directory.
        *   `output_path` (str, optional): Output directory. Default: `"dist/{name}"`.
        *   `dependencies` (list[str], optional): List of dependency names.
    *   **Returns**: `BuildTarget` dataclass instance.

8.  **`create_docker_build_target(name: str, source_path: str, dockerfile_path: str = "Dockerfile", image_tag: str = None) -> BuildTarget`**
    *   **Description**: Create a Docker build target with steps to build and test a Docker image.
    *   **Arguments**:
        *   `name` (str): Target name.
        *   `source_path` (str): Path to source directory.
        *   `dockerfile_path` (str, optional): Path to Dockerfile. Default: `"Dockerfile"`.
        *   `image_tag` (str, optional): Docker image tag. Default: `"{name}:latest"`.
    *   **Returns**: `BuildTarget` dataclass instance.

9.  **`create_static_build_target(name: str, source_path: str, output_path: str = None, build_command: str = "npm run build") -> BuildTarget`**
    *   **Description**: Create a static site build target with steps for npm install, build, and optional optimization.
    *   **Arguments**:
        *   `name` (str): Target name.
        *   `source_path` (str): Path to source directory.
        *   `output_path` (str, optional): Output directory. Default: `"dist/{name}"`.
        *   `build_command` (str, optional): Build command. Default: `"npm run build"`.
    *   **Returns**: `BuildTarget` dataclass instance.

10. **`get_available_build_types() -> list[BuildType]`**
    *   **Description**: Get the list of available build types.
    *   **Returns**: List of `BuildType` enum members.

11. **`get_available_environments() -> list[BuildEnvironment]`**
    *   **Description**: Get the list of available build environments.
    *   **Returns**: List of `BuildEnvironment` enum members.

## Data Models

### Enums

#### `BuildType(Enum)`
Types of builds supported:
- `PYTHON = "python"`
- `NODEJS = "nodejs"`
- `DOCKER = "docker"`
- `STATIC = "static"`
- `DOCUMENTATION = "documentation"`
- `TESTING = "testing"`
- `PACKAGING = "packaging"`
- `DEPLOYMENT = "deployment"`

#### `BuildStatus(Enum)`
Build status states:
- `PENDING = "pending"`
- `RUNNING = "running"`
- `SUCCESS = "success"`
- `FAILED = "failed"`
- `CANCELLED = "cancelled"`
- `SKIPPED = "skipped"`

#### `BuildEnvironment(Enum)`
Build environments:
- `DEVELOPMENT = "development"`
- `STAGING = "staging"`
- `PRODUCTION = "production"`
- `TESTING = "testing"`

#### `DependencyType(Enum)`
Types of dependencies:
- `RUNTIME = "runtime"`
- `DEVELOPMENT = "development"`
- `BUILD = "build"`
- `OPTIONAL = "optional"`

### Dataclasses

#### `BuildStep`
Individual build step definition:
```python
@dataclass
class BuildStep:
    name: str
    command: str
    working_dir: str | None = None
    environment: dict[str, str] = field(default_factory=dict)
    dependencies: list[str] = field(default_factory=list)
    timeout: int = 300  # seconds
    retry_count: int = 0
    required: bool = True
    parallel: bool = False
    condition: str | None = None  # Command to check if step should run
```

#### `BuildTarget`
Build target definition:
```python
@dataclass
class BuildTarget:
    name: str
    build_type: BuildType
    source_path: str
    output_path: str
    dependencies: list[str] = field(default_factory=list)
    environment: BuildEnvironment = BuildEnvironment.DEVELOPMENT
    config: dict[str, Any] = field(default_factory=dict)
    steps: list[BuildStep] = field(default_factory=list)
```

#### `BuildResult`
Result of a build operation:
```python
@dataclass
class BuildResult:
    target_name: str
    status: BuildStatus
    start_time: datetime
    end_time: datetime | None = None
    duration: float | None = None
    output: str = ""
    error: str = ""
    artifacts: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
```

#### `Dependency`
Dependency definition:
```python
@dataclass
class Dependency:
    name: str
    version: str
    dep_type: DependencyType
    source: str = "pypi"  # pypi, npm, git, local, etc.
    install_command: str | None = None
    check_command: str | None = None
```

### BuildManager Class

**`BuildManager(project_root: str = None, config_path: str = None)`**

Main build management class providing comprehensive build orchestration.

**Constructor Arguments**:
- `project_root` (str, optional): Root directory of the project. Default: current working directory.
- `config_path` (str, optional): Path to build configuration file (YAML or JSON). Default: `{project_root}/build.yaml`.

**Key Methods**:

| Method | Signature | Returns | Description |
|--------|-----------|---------|-------------|
| `add_build_target` | `(target: BuildTarget) -> bool` | `bool` | Add a build target to the manager |
| `add_dependency` | `(dependency: Dependency) -> bool` | `bool` | Add a dependency to the manager |
| `check_dependencies` | `() -> dict[str, bool]` | `dict[str, bool]` | Check if all dependencies are available |
| `install_dependencies` | `(force: bool = False) -> dict[str, bool]` | `dict[str, bool]` | Install missing dependencies |
| `build_target` | `(target_name: str, environment: BuildEnvironment = None) -> BuildResult` | `BuildResult` | Build a specific target |
| `build_all_targets` | `(environment: BuildEnvironment = None) -> list[BuildResult]` | `list[BuildResult]` | Build all targets |
| `clean_build` | `(target_name: str = None) -> bool` | `bool` | Clean build artifacts |
| `package_artifacts` | `(target_name: str, output_path: str = None) -> str` | `str` | Package build artifacts as tar.gz |
| `get_build_summary` | `() -> dict[str, Any]` | `dict` | Get summary of all builds |
| `export_config` | `(output_path: str) -> bool` | `bool` | Export current configuration to file |

## Authentication & Authorization

Direct API access, if exposed externally from the Codomyrmex system, would require appropriate authentication and authorization mechanisms. Within the system, MCP tool usage is typically governed by the calling agent's permissions. These Python APIs assume they are called in an already authenticated and authorized context.

## Rate Limiting

As these API functions can trigger resource-intensive operations (builds, subprocess calls), any external exposure should be protected by rate limiting. Internal usage should be mindful of resource consumption.

## Versioning

API versioning for these Python functions will follow standard Python library practices. Significant changes will be noted in the module's `CHANGELOG.md`.
## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../../../docs/README.md)
- **Home**: [Root README](../../../README.md)
