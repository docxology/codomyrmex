# Codomyrmex Agents — src/codomyrmex/build_synthesis

## Signposting
- **Parent**: [codomyrmex](../AGENTS.md)
- **Self**: [Build Synthesis Agents](AGENTS.md)
- **Children**:
    - [docs](docs/AGENTS.md)
    - [tests](tests/AGENTS.md)
- **Key Artifacts**:
    - [Functional Spec](SPEC.md)
    - [Human Readme](README.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: December 2025

## Purpose

Core Service Layer module providing build automation, dependency management, and deployment orchestration capabilities for the Codomyrmex platform. This module handles the synthesis and orchestration of build pipelines across multiple technologies and environments.

The build_synthesis module serves as the deployment and build automation layer, enabling consistent and reliable software builds across the entire platform ecosystem.

## Module Overview

### Key Capabilities
- **Build Orchestration**: Multi-step build pipeline management
- **Dependency Resolution**: Automatic dependency management and installation
- **Artifact Synthesis**: Creation of deployable build artifacts
- **Environment Management**: Cross-platform build environment configuration
- **Build Validation**: Automated quality checks and validation

### Key Features
- Support for multiple build types (Python, Docker, static sites)
- Configurable build pipelines with dependencies
- Automated build artifact generation
- Build environment validation and setup
- Integration with deployment systems

## Function Signatures

### Build Orchestration Functions

```python
def check_build_environment() -> None
```

Check if the build environment is properly configured with required tools.

**Returns:** None - Logs status of build tools availability

```python
def run_build_command(command: list[str], cwd: str = None) -> tuple[bool, str, str]
```

Execute a build command and capture output.

**Parameters:**
- `command` (list[str]): Command to execute as list of strings
- `cwd` (str): Working directory to run command in. If None, uses current directory

**Returns:** `tuple[bool, str, str]` - (success: bool, stdout: str, stderr: str)

```python
def synthesize_build_artifact(
    source_path: str,
    output_path: str,
    artifact_type: str = "package",
    metadata: dict[str, Any] = None,
) -> dict[str, Any]
```

Create a build artifact from source files.

**Parameters:**
- `source_path` (str): Path to source files
- `output_path` (str): Path where artifact should be created
- `artifact_type` (str): Type of artifact ("package", "executable", "archive"). Defaults to "package"
- `metadata` (dict[str, Any]): Additional metadata for the artifact

**Returns:** `dict[str, Any]` - Artifact creation result with paths and metadata

```python
def validate_build_output(output_path: str) -> dict[str, Any]
```

Validate that build outputs meet quality standards.

**Parameters:**
- `output_path` (str): Path to build output to validate

**Returns:** `dict[str, Any]` - Validation results with checks performed and results

```python
def orchestrate_build_pipeline(build_config: dict[str, Any]) -> dict[str, Any]
```

Execute a complete build pipeline with multiple steps and dependencies.

**Parameters:**
- `build_config` (dict[str, Any]): Build configuration including steps, dependencies, and parameters

**Returns:** `dict[str, Any]` - Build pipeline results with step outcomes and final artifacts

### Build Target Creation Functions

```python
def create_python_build_target(
    name: str, source_path: str, output_path: str = None, dependencies: list[str] = None
) -> BuildTarget
```

Create a Python package build target with standard steps.

**Parameters:**
- `name` (str): Name of the build target
- `source_path` (str): Path to Python source files
- `output_path` (str): Output path for built artifacts. If None, uses "dist/{name}"
- `dependencies` (list[str]): List of dependencies to install

**Returns:** `BuildTarget` - Configured Python build target

```python
def create_docker_build_target(
    name: str,
    source_path: str,
    dockerfile_path: str = "Dockerfile",
    output_path: str = None,
    build_args: dict[str, str] = None,
) -> BuildTarget
```

Create a Docker image build target.

**Parameters:**
- `name` (str): Name of the build target
- `source_path` (str): Path to source files for Docker context
- `dockerfile_path` (str): Path to Dockerfile. Defaults to "Dockerfile"
- `output_path` (str): Output path for built image. If None, uses default registry path
- `build_args` (dict[str, str]): Docker build arguments

**Returns:** `BuildTarget` - Configured Docker build target

```python
def create_static_build_target(
    name: str,
    source_path: str,
    build_command: str = "npm run build",
    output_path: str = "dist",
    dependencies: list[str] = None,
) -> BuildTarget
```

Create a static site build target.

**Parameters:**
- `name` (str): Name of the build target
- `source_path` (str): Path to source files
- `build_command` (str): Build command to execute. Defaults to "npm run build"
- `output_path` (str): Output directory for built files. Defaults to "dist"
- `dependencies` (list[str]): List of dependencies to install

**Returns:** `BuildTarget` - Configured static site build target

### Build Management Functions

```python
def get_available_build_types() -> list[BuildType]
```

Get list of supported build types.

**Returns:** `list[BuildType]` - Available build type options

```python
def get_available_environments() -> list[BuildEnvironment]
```

Get list of supported build environments.

**Returns:** `list[BuildEnvironment]` - Available build environment options

```python
def trigger_build(
    build_target: BuildTarget,
    environment: BuildEnvironment = BuildEnvironment.LOCAL,
    options: dict[str, Any] = None,
) -> BuildResult
```

Execute a build using the specified target and environment.

**Parameters:**
- `build_target` (BuildTarget): Build target to execute
- `environment` (BuildEnvironment): Build environment to use. Defaults to BuildEnvironment.LOCAL
- `options` (dict[str, Any]): Additional build options

**Returns:** `BuildResult` - Build execution results

## Data Structures

### BuildTarget
```python
class BuildTarget:
    name: str
    build_type: BuildType
    source_path: str
    output_path: str
    dependencies: list[str]
    steps: list[BuildStep]
    metadata: dict[str, Any]
```

Build target configuration containing all information needed to execute a build.

### BuildStep
```python
class BuildStep:
    name: str
    command: str
    required: bool = True
    working_directory: str = None
    environment_variables: dict[str, str] = None
    timeout: int = None
```

Individual step within a build pipeline.

### BuildResult
```python
class BuildResult:
    success: bool
    target_name: str
    output_path: str
    artifacts: list[str]
    duration: float
    steps_completed: list[str]
    steps_failed: list[str]
    error_message: str = None
    logs: list[str]
```

Results of a build execution.

### BuildManager
```python
class BuildManager:
    def __init__(self, config: dict[str, Any] = None)

    def add_target(self, target: BuildTarget) -> None
    def get_target(self, name: str) -> BuildTarget
    def list_targets(self) -> list[str]
    def execute_target(self, name: str, environment: BuildEnvironment = BuildEnvironment.LOCAL) -> BuildResult
    def validate_targets(self) -> list[str]
```

Main build management class for coordinating multiple build targets.

### Enums

```python
class BuildType(Enum):
    PYTHON = "python"
    DOCKER = "docker"
    STATIC = "static"
    EXECUTABLE = "executable"
    ARCHIVE = "archive"

class BuildStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"

class BuildEnvironment(Enum):
    LOCAL = "local"
    CI_CD = "ci_cd"
    CONTAINER = "container"
    REMOTE = "remote"

class DependencyType(Enum):
    PYTHON = "python"
    SYSTEM = "system"
    NPM = "npm"
    APT = "apt"
```

## Active Components

### Core Implementation
- `__init__.py` – Module initialization and public API exports
- `build_orchestrator.py` – Build pipeline orchestration and execution
- `build_manager.py` – Build target management and configuration

### Documentation
- `README.md` – Module usage and overview
- `API_SPECIFICATION.md` – Complete API documentation
- `USAGE_EXAMPLES.md` – Practical usage demonstrations
- `MCP_TOOL_SPECIFICATION.md` – AI agent tool specifications
- `SECURITY.md` – Security considerations for build processes
- `CHANGELOG.md` – Version history and updates

### Supporting Files
- `requirements.txt` – Module dependencies (build tools, packaging libraries)
- `docs/` – Additional build documentation and guides
- `tests/` – Comprehensive test suite for build functionality

## Operating Contracts

### Universal Build Protocols

All build synthesis within the Codomyrmex platform must:

1. **Reproducible Builds** - Build outputs must be consistent across environments
2. **Dependency Management** - Clear dependency declarations and automatic resolution
3. **Quality Assurance** - Automated validation of build outputs
4. **Environment Agnostic** - Builds work across different environments
5. **Logging and Monitoring** - Comprehensive build logging and monitoring

### Module-Specific Guidelines

#### Build Orchestration
- Support complex multi-step build pipelines
- Handle build dependencies and ordering correctly
- Provide clear error messages and failure recovery
- Support parallel build execution where appropriate

#### Build Targets
- Define clear, reusable build target templates
- Support multiple output formats and artifact types
- Include validation steps in build pipelines
- Document build requirements and prerequisites

#### Build Management
- Provide build status tracking and reporting
- Support build cancellation and cleanup
- Enable build configuration management
- Integrate with CI/CD systems and deployment pipelines

## Navigation Links
- **Human Documentation**: [README.md](README.md)
- **Functional Specification**: [SPEC.md](SPEC.md)

### Module Documentation
- **Module Overview**: [README.md](README.md) - Complete module documentation
- **API Reference**: [API_SPECIFICATION.md](API_SPECIFICATION.md) - Detailed API specification (if applicable)
- **Usage Examples**: [USAGE_EXAMPLES.md](USAGE_EXAMPLES.md) - Practical usage demonstrations (if applicable)

### Platform Navigation
- **Parent Directory**: [codomyrmex](../README.md) - Package overview
- **Project Root**: [README](../../../README.md) - Main project documentation
- **Source Root**: [src](../../README.md) - Source code documentation