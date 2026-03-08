"""
Environment Setup Module for Codomyrmex.

This module provides tools for validating the environment, checking dependencies,
managing environment variables, and integrating with the uv package manager.
"""

import contextlib
from collections.abc import Callable
from typing import Any

from .dependency_resolver import (
    Conflict,
    DependencyInfo,
    DependencyResolver,
    install_dependencies,
)
from .env_checker import (
    APIKeyReport,
    DependencyStatus,
    ValidationReport,
    check_and_setup_env_vars,
    check_api_keys,
    check_dependencies,
    ensure_dependencies_installed,
    generate_environment_report,
    get_uv_path,
    is_uv_available,
    is_uv_environment,
    validate_environment,
    validate_environment_completeness,
    validate_python_version,
)

# Shared schemas for cross-module interop
with contextlib.suppress(ImportError):
    from codomyrmex.validation.schemas import Result, ResultStatus


def cli_commands() -> dict[str, dict[str, str | Callable]]:
    """Return CLI commands for the environment_setup module."""
    return {
        "check": {
            "help": "Validate environment setup (Python version, uv, env vars)",
            "handler": lambda **kwargs: print(
                f"Python valid: {validate_python_version()}\n"
                f"uv available: {is_uv_available()}\n"
                f"uv environment: {is_uv_environment()}\n"
                f"Environment report:\n{generate_environment_report()}"
            ),
        },
        "deps": {
            "help": "List and verify installed dependencies",
            "handler": lambda **kwargs: print(
                f"Dependencies status: {ensure_dependencies_installed()}"
            ),
        },
    }


__all__ = [
    "APIKeyReport",
    "Conflict",
    "DependencyInfo",
    "DependencyResolver",
    "DependencyStatus",
    "ValidationReport",
    "check_and_setup_env_vars",
    "check_api_keys",
    "check_dependencies",
    "cli_commands",
    "ensure_dependencies_installed",
    "generate_environment_report",
    "get_uv_path",
    "install_dependencies",
    "is_uv_available",
    "is_uv_environment",
    "validate_environment",
    "validate_environment_completeness",
    "validate_python_version",
]
