# Environment Setup Module

**Version**: v0.1.0 | **Status**: Active

Development environment validation, dependency management, and uv integration.

## Quick Start

```python
from codomyrmex.environment_setup import (
    is_uv_available,
    is_uv_environment,
    ensure_dependencies_installed,
    check_and_setup_env_vars,
    validate_python_version,
)

# Validate Python version
validate_python_version(min_version="3.11")

# Check uv package manager
if is_uv_available():
    print("uv is installed")
if is_uv_environment():
    print("Running in uv-managed environment")

# Ensure dependencies are installed
ensure_dependencies_installed(["pydantic", "httpx", "pytest"])

# Setup and validate environment variables
missing = check_and_setup_env_vars(
    required=["OPENAI_API_KEY", "DATABASE_URL"],
    optional=["DEBUG", "LOG_LEVEL"]
)
if missing:
    print(f"Missing required variables: {missing}")
```

## Exports

| Function | Description |
|----------|-------------|
| `validate_python_version(min)` | Check Python meets minimum version |
| `is_uv_available()` | Check if uv package manager is installed |
| `is_uv_environment()` | Check if running in uv environment |
| `ensure_dependencies_installed(list)` | Install missing packages |
| `check_and_setup_env_vars(req, opt)` | Validate and load env vars from .env |

## Navigation

- [SPEC](SPEC.md) | [AGENTS](AGENTS.md) | [PAI](PAI.md)
