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
"""

from .env_checker import (
    check_and_setup_env_vars,
    ensure_dependencies_installed,
    is_uv_available,
    is_uv_environment,
)

__all__ = [
    "is_uv_available",
    "is_uv_environment",
    "ensure_dependencies_installed",
    "check_and_setup_env_vars",
]
