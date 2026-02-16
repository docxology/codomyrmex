"""Backward-compatible shim for build_manager.

The actual implementation has moved to ``build_synthesis.core.build_manager``.
This module re-exports every public name so that existing imports such as
``from codomyrmex.build_synthesis.build_manager import BuildManager`` continue
to work without modification.
"""

from .core.build_manager import (  # noqa: F401
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
    "BuildEnvironment",
    "BuildManager",
    "BuildResult",
    "BuildStatus",
    "BuildStep",
    "BuildTarget",
    "BuildType",
    "Dependency",
    "DependencyType",
    "create_docker_build_target",
    "create_python_build_target",
    "create_static_build_target",
    "get_available_build_types",
    "get_available_environments",
    "trigger_build",
]
