# Environment Setup Module Documentation

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Automated development environment provisioning with Python, Node.js, and system dependency management.

## Key Features

- `ensure_dependencies_installed()` — Check if primary dependencies are installed and accessible.
- `check_and_setup_env_vars()` — Load environment variables from a .env file.
- `validate_python_version()` — Validate that the Python version meets minimum requirements.
- `is_uv_available()` — Check if the 'uv' package manager is available in the system PATH.

## Quick Start

```python
from codomyrmex.environment_setup import ensure_dependencies_installed, check_and_setup_env_vars, validate_python_version

result = ensure_dependencies_installed()
```

## Source Files

- `env_checker.py`

## Directory Contents

| File | Description |
|------|-------------|
| `README.md` | This documentation |
| `AGENTS.md` | Agent coordination guide |
| `SPEC.md` | Technical specification |
| `tutorials/` | Tutorials |


## Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k environment_setup -v
```

## Navigation

- **Source**: [src/codomyrmex/environment_setup/](../../../src/codomyrmex/environment_setup/)
- **Parent**: [Modules](../README.md)
