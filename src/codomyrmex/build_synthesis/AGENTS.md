# Codomyrmex Agents — src/codomyrmex/build_synthesis

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose

The Build Synthesis module provides comprehensive build automation, dependency management, artifact synthesis, and deployment orchestration capabilities for the Codomyrmex ecosystem. It supports multiple build types (Python, Node.js, Docker, static sites), manages build environments, handles dependency installation and verification, and provides build pipeline orchestration with environment-specific configurations.

## Active Components

### Core Build Management

- `build_manager.py` - Advanced build management with targets, steps, and dependencies
  - Key Classes: `BuildManager`, `BuildTarget`, `BuildStep`, `BuildResult`, `Dependency`
  - Key Functions: `create_python_build_target()`, `create_docker_build_target()`, `create_static_build_target()`, `trigger_build()`, `get_available_build_types()`, `get_available_environments()`
  - Key Enums: `BuildType`, `BuildStatus`, `BuildEnvironment`, `DependencyType`

### Build Orchestration

- `build_orchestrator.py` - Build pipeline orchestration and artifact synthesis
  - Key Functions: `check_build_environment()`, `run_build_command()`, `synthesize_build_artifact()`, `validate_build_output()`, `orchestrate_build_pipeline()`

## Key Classes and Functions

| Class/Function | Module | Purpose |
| :--- | :--- | :--- |
| `BuildManager` | build_manager | Main build management class with target and dependency handling |
| `BuildTarget` | build_manager | Build target definition with source, output, and steps |
| `BuildStep` | build_manager | Individual build step with command, timeout, and retry settings |
| `BuildResult` | build_manager | Result of a build operation with status, duration, and artifacts |
| `Dependency` | build_manager | Dependency definition with version, type, and install commands |
| `build_target()` | build_manager | Execute a specific build target |
| `build_all_targets()` | build_manager | Execute all configured build targets |
| `check_dependencies()` | build_manager | Verify all dependencies are available |
| `install_dependencies()` | build_manager | Install missing dependencies |
| `package_artifacts()` | build_manager | Package build artifacts into distributable archives |
| `clean_build()` | build_manager | Clean build artifacts |
| `orchestrate_build_pipeline()` | build_orchestrator | Execute complete build pipeline with stages |
| `synthesize_build_artifact()` | build_orchestrator | Create build artifacts from source code |
| `validate_build_output()` | build_orchestrator | Validate build output meets expectations |

## Operating Contracts

1. **Logging**: All build operations use `logging_monitoring` for structured logging
2. **Performance Monitoring**: Build operations are decorated with `@monitor_performance` for tracking
3. **Configuration**: Build configuration loaded from YAML/JSON files with sensible defaults
4. **Environment Isolation**: Build steps execute with isolated environment variables
5. **Command Safety**: Commands are parsed with `shlex.split()` to avoid shell injection
6. **Timeout Handling**: All subprocess calls include configurable timeouts
7. **Error Recovery**: Build steps support retry counts and conditional execution
8. **Artifact Management**: Build artifacts are packaged as tar.gz archives

## Integration Points

- **logging_monitoring** - All build operations log via centralized logger
- **performance** - Build operations tracked with performance monitoring
- **environment_setup** - Environment and dependency verification
- **containerization** - Docker build target integration

## Signposting

### Document Hierarchy

- **Self**: [AGENTS.md](AGENTS.md)
- **Parent**: [src/codomyrmex/AGENTS.md](../AGENTS.md)
- **Project Root**: [../../../AGENTS.md](../../../AGENTS.md)

### Sibling Modules

| Module | AGENTS.md | Purpose |
| :--- | :--- | :--- |
| ci_cd_automation | [../ci_cd_automation/AGENTS.md](../ci_cd_automation/AGENTS.md) | CI/CD pipelines |
| containerization | [../containerization/AGENTS.md](../containerization/AGENTS.md) | Docker/Kubernetes |
| environment_setup | [../environment_setup/AGENTS.md](../environment_setup/AGENTS.md) | Environment configuration |

### Child Directories

| Directory | Purpose |
| :--- | :--- |
| (none) | This module has no subdirectories |

### Related Documentation

- [README.md](README.md) - User documentation
- [API_SPECIFICATION.md](API_SPECIFICATION.md) - API documentation
- [MCP_TOOL_SPECIFICATION.md](MCP_TOOL_SPECIFICATION.md) - MCP tool specifications
- [USAGE_EXAMPLES.md](USAGE_EXAMPLES.md) - Usage examples
- [SPEC.md](SPEC.md) - Functional specification
- [SECURITY.md](SECURITY.md) - Security considerations
- [CHANGELOG.md](CHANGELOG.md) - Change history
