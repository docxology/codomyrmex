"""
Build Synthesis Module for Codomyrmex.

The Build Synthesis module provides build automation, dependency management,
artifact synthesis, and deployment orchestration capabilities within the Codomyrmex ecosystem.

Integration:
- Uses `logging_monitoring` for all logging (ensure `setup_logging()` is called in your main app).
- Relies on `environment_setup` for environment and dependency checks.

Subpackages:
- core/       - Build management classes, data structures, and convenience functions
- pipeline/   - Build orchestration and pipeline execution capabilities

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

# Shared schemas for cross-module interop
try:
    from codomyrmex.schemas import Result, ResultStatus
except ImportError:
    Result = None
    ResultStatus = None

from .core import (
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
from .pipeline import (
    check_build_environment,
    orchestrate_build_pipeline,
    run_build_command,
    synthesize_build_artifact,
    validate_build_output,
)

def cli_commands():
    """Return CLI commands for the build_synthesis module."""
    def _list_builders():
        build_types = get_available_build_types()
        print("Available build types:")
        for bt in build_types:
            print(f"  {bt}")
        environments = get_available_environments()
        print("Available build environments:")
        for env in environments:
            print(f"  {env}")

    def _build(path=None):
        import os
        target = path or os.getcwd()
        print(f"Running build for: {target}")
        try:
            result = trigger_build(target)
            if isinstance(result, dict):
                for key, value in result.items():
                    print(f"  {key}: {value}")
            else:
                print(f"  Result: {result}")
        except Exception as e:
            print(f"Build error: {e}")

    return {
        "builders": _list_builders,
        "build": _build,
    }


__all__ = [
    "cli_commands",
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
