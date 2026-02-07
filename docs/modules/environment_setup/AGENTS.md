# Environment Setup Module — Agent Coordination

## Purpose

Environment Setup Module for Codomyrmex.

## Key Capabilities

- Environment Setup operations and management

## Agent Usage Patterns

```python
from codomyrmex.environment_setup import *

# Agent uses environment setup capabilities
```

## Integration Points

- **Source**: [src/codomyrmex/environment_setup/](../../../src/codomyrmex/environment_setup/)
- **Docs**: [Module Documentation](README.md)
- **Spec**: [Technical Specification](SPEC.md)


## Key Components

- **`ensure_dependencies_installed()`** — Check if primary dependencies are installed and accessible.
- **`check_and_setup_env_vars()`** — Load environment variables from a .env file.
- **`validate_python_version()`** — Validate that the Python version meets minimum requirements.
- **`is_uv_available()`** — Check if the 'uv' package manager is available in the system PATH.
- **`is_uv_environment()`** — Check if the current Python interpreter is running within a uv-managed environment.

## Testing Guidelines

```bash
uv run python -m pytest src/codomyrmex/tests/ -k environment_setup -v
```

- Run tests before and after making changes.
- Ensure all existing tests pass before submitting.
