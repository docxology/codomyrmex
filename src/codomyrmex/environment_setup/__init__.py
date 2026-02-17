"""
Environment Setup Module for Codomyrmex.

For general project development environment setup instructions (covering
prerequisites, cloning, virtual environments, Python dependencies, API keys,
and other essential configurations).

Integration:
- Uses `logging_monitoring` for all logging (ensure `setup_logging()` is called in your main app).
- Core module that other modules depend on for environment validation.

Available functions:
- is_uv_available
- is_uv_environment
- ensure_dependencies_installed
- check_and_setup_env_vars
- validate_python_version
"""

from .env_checker import (
    check_and_setup_env_vars,
    ensure_dependencies_installed,
    is_uv_available,
    is_uv_environment,
    validate_python_version,
)

# Shared schemas for cross-module interop
try:
    from codomyrmex.validation.schemas import Result, ResultStatus
except ImportError:
    Result = None
    ResultStatus = None


def cli_commands():
    """Return CLI commands for the environment_setup module."""
    return {
        "check": {
            "help": "Validate environment setup (Python version, uv, env vars)",
            "handler": lambda **kwargs: print(
                f"Python valid: {validate_python_version()}\n"
                f"uv available: {is_uv_available()}\n"
                f"uv environment: {is_uv_environment()}"
            ),
        },
        "deps": {
            "help": "List and verify installed dependencies",
            "handler": lambda **kwargs: print(
                f"Dependencies installed: {ensure_dependencies_installed()}"
            ),
        },
    }


__all__ = [
    "is_uv_available",
    "is_uv_environment",
    "ensure_dependencies_installed",
    "check_and_setup_env_vars",
    "validate_python_version",
    "cli_commands",
]
