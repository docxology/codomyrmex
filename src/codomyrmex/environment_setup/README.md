# environment_setup

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Foundation-layer module that validates and configures the development environment for Codomyrmex. Provides functions to detect the `uv` package manager, verify Python version compatibility (requires 3.10+), check that required dependencies (`kit`, `python-dotenv`) are installed, and load environment variables from `.env` files. This is a core dependency that other modules rely on for environment validation.

## Key Exports

- **`is_uv_available()`** -- Checks whether the `uv` package manager binary is available on the system PATH using `shutil.which`
- **`is_uv_environment()`** -- Returns True if running inside a uv-managed virtual environment (checks `VIRTUAL_ENV` env var) or if uv is installed
- **`ensure_dependencies_installed()`** -- Verifies that required dependencies (`kit` and `python-dotenv`) are importable, prints status messages, and returns a boolean
- **`check_and_setup_env_vars()`** -- Loads environment variables from a `.env` file in the specified repository root using `python-dotenv`, returns True on success
- **`validate_python_version()`** -- Validates that the current Python interpreter meets the minimum version requirement (3.10+), takes no arguments

## Directory Contents

- `env_checker.py` -- All environment validation functions (uv detection, dependency checks, Python version, env var loading)
- `scripts/` -- Setup and automation scripts
- `requirements.txt` -- Module-specific dependency list (deprecated, use pyproject.toml)

## Navigation

- **Full Documentation**: [docs/modules/environment_setup/](../../../docs/modules/environment_setup/)
- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: ../../../README.md
