"""Core build management components for Codomyrmex Build Synthesis.

This subpackage contains the primary build management classes, data structures,
and convenience functions for defining and executing build targets.

Classes:
    BuildManager: Main build management class
    BuildTarget: Build target definition
    BuildStep: Individual build step definition
    BuildResult: Result of a build operation
    Dependency: Dependency definition

Enums:
    BuildType: Types of builds supported
    BuildStatus: Build status states
    BuildEnvironment: Build environments
    DependencyType: Types of dependencies

Functions:
    create_python_build_target: Create a Python build target
    create_docker_build_target: Create a Docker build target
    create_static_build_target: Create a static site build target
    get_available_build_types: Get list of available build types
    get_available_environments: Get list of available build environments
    trigger_build: Trigger a build process
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

__all__ = [
    "BuildManager",
    "BuildTarget",
    "BuildStep",
    "BuildResult",
    "Dependency",
    "BuildType",
    "BuildStatus",
    "BuildEnvironment",
    "DependencyType",
    "create_python_build_target",
    "create_docker_build_target",
    "create_static_build_target",
    "get_available_build_types",
    "get_available_environments",
    "trigger_build",
]
