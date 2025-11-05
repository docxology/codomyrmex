"""
Build Synthesis Module for Codomyrmex.

The Build Synthesis module provides comprehensive build automation, dependency management,
artifact synthesis, and deployment orchestration capabilities within the Codomyrmex ecosystem.

Integration:
- Uses `logging_monitoring` for all logging (ensure `setup_logging()` is called in your main app).
- Relies on `environment_setup` for environment and dependency checks.

Available functions:
- check_build_environment: Check build environment setup
- run_build_command: Execute build commands
- synthesize_build_artifact: Create build artifacts
- validate_build_output: Validate build outputs
- orchestrate_build_pipeline: Orchestrate complete build pipelines
- create_python_build_target: Create Python build target
- create_docker_build_target: Create Docker build target
- create_static_build_target: Create static site build target
- get_available_build_types: Get available build types
- get_available_environments: Get available build environments

Data structures:
- BuildManager: Main build management class
- BuildTarget: Build target definition
- BuildStep: Individual build step definition
- BuildResult: Result of a build operation
- Dependency: Dependency definition
- BuildType: Types of builds supported
- BuildStatus: Build status states
- BuildEnvironment: Build environments
- DependencyType: Types of dependencies
"""

from .build_manager import (
    BuildEnvironment,
    BuildManager,
    BuildResult,
    BuildStatus,
    BuildStep,
    BuildTarget,
    BuildType,
    Dependency,
    DependencyType,
    create_docker_build_target,
    create_python_build_target,
    create_static_build_target,
    get_available_build_types,
    get_available_environments,
    trigger_build,
)
from .build_orchestrator import (
    check_build_environment,
    orchestrate_build_pipeline,
    run_build_command,
    synthesize_build_artifact,
    validate_build_output,
)

__all__ = [
    # Original functions
    "check_build_environment",
    "run_build_command",
    "synthesize_build_artifact",
    "validate_build_output",
    "orchestrate_build_pipeline",
    # New build management functions
    "BuildManager",
    "create_python_build_target",
    "create_docker_build_target",
    "create_static_build_target",
    "get_available_build_types",
    "get_available_environments",
    "trigger_build",
    # Data structures
    "BuildTarget",
    "BuildStep",
    "BuildResult",
    "Dependency",
    "BuildType",
    "BuildStatus",
    "BuildEnvironment",
    "DependencyType",
]
