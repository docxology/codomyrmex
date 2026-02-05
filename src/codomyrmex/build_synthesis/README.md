# build_synthesis

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Build automation module providing multi-language build management, artifact synthesis, and pipeline orchestration. The `BuildManager` class manages build targets with typed dependencies, steps, and environment configurations. Factory functions create pre-configured targets for Python, Docker, and static site builds. The `build_orchestrator` module provides environment checking, command execution, artifact synthesis, output validation, and full pipeline orchestration. Supports three build types (application, library, service), multiple environments (development, staging, production), and typed dependency tracking.

## Key Exports

### Orchestration Functions

- **`check_build_environment()`** -- Verify that the build environment has required tools and dependencies
- **`run_build_command()`** -- Execute a build command with output capture and error handling
- **`synthesize_build_artifact()`** -- Generate a build artifact from source and configuration
- **`validate_build_output()`** -- Validate that build output meets expected criteria
- **`orchestrate_build_pipeline()`** -- Run a complete build pipeline end-to-end

### Build Management

- **`BuildManager`** -- Central class for managing build targets, dependencies, and execution
- **`trigger_build()`** -- Trigger a build for a specific target
- **`create_python_build_target()`** -- Create a pre-configured Python build target (wheel/sdist)
- **`create_docker_build_target()`** -- Create a pre-configured Docker image build target
- **`create_static_build_target()`** -- Create a pre-configured static site build target
- **`get_available_build_types()`** -- List all supported build types
- **`get_available_environments()`** -- List all supported build environments

### Data Structures

- **`BuildTarget`** -- Build target definition with name, type, source path, steps, and dependencies
- **`BuildStep`** -- Individual step within a build (command, working directory, environment)
- **`BuildResult`** -- Result of a build execution with status, output, and timing
- **`Dependency`** -- Dependency definition with name, version constraint, and type
- **`BuildType`** -- Enum of build types: application, library, service
- **`BuildStatus`** -- Enum of build states: pending, running, success, failure, cancelled
- **`BuildEnvironment`** -- Enum of target environments: development, staging, production
- **`DependencyType`** -- Enum of dependency types: runtime, build, dev, optional

## Directory Contents

- `__init__.py` - Module entry point aggregating build manager and orchestrator exports
- `build_manager.py` - `BuildManager`, build target factories, data structures, and enums
- `build_orchestrator.py` - Pipeline orchestration, environment checking, and artifact synthesis
- `requirements.txt` - Module-specific dependencies

## Navigation

- **Full Documentation**: [docs/modules/build_synthesis/](../../../docs/modules/build_synthesis/)
- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: ../../../README.md
