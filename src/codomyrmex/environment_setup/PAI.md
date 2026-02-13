# Personal AI Infrastructure — Environment Setup Module

**Version**: v0.2.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The Environment Setup module validates the development environment, checks dependencies, and ensures the codomyrmex ecosystem can run correctly. It is a **Foundation Layer** module that other modules depend on for environment validation.

## PAI Capabilities

### Environment Validation

Validate that the runtime environment meets requirements:

```python
from codomyrmex.environment_setup import (
    validate_python_version,
    is_uv_available,
    is_uv_environment,
    ensure_dependencies_installed,
    check_and_setup_env_vars,
)

# Check Python version compatibility
valid = validate_python_version()  # True if Python >= required version

# Check uv package manager
uv_available = is_uv_available()      # True if uv is installed
uv_env = is_uv_environment()          # True if running inside uv venv

# Verify dependencies
deps_ok = ensure_dependencies_installed()  # True if all deps satisfied

# Validate and setup environment variables
check_and_setup_env_vars()  # Checks required env vars, prompts if missing
```

### CLI Commands

```bash
codomyrmex environment_setup check   # Validate Python version, uv, env vars
codomyrmex environment_setup deps    # List and verify installed dependencies
```

## Key Exports

| Export | Type | Purpose |
|--------|------|---------|
| `validate_python_version()` | Function | Check Python version meets minimum requirement |
| `is_uv_available()` | Function | Check if `uv` package manager is installed |
| `is_uv_environment()` | Function | Check if running inside a `uv`-managed virtual environment |
| `ensure_dependencies_installed()` | Function | Verify all required dependencies are installed |
| `check_and_setup_env_vars()` | Function | Validate and setup required environment variables |
| `cli_commands()` | Function | CLI command registration |

## PAI Algorithm Phase Mapping

| Phase | Environment Setup Contribution |
|-------|-------------------------------|
| **OBSERVE** | `validate_python_version()`, `is_uv_available()` — assess environment state |
| **VERIFY** | `ensure_dependencies_installed()` — confirm all dependencies present before execution |
| **EXECUTE** | `check_and_setup_env_vars()` — ensure environment is ready for tool execution |

## Dependencies

- Uses `logging_monitoring` for all logging
- Core module that other modules depend on (upward dependency only)
- Integrates with `python-dotenv` for `.env` file support

## Architecture Role

**Foundation Layer** — One of the 4 foundation modules. Called early in startup sequences and by modules that need to validate their runtime environment before operating.

## Navigation

- **Self**: [PAI.md](PAI.md)
- **Parent**: [../PAI.md](../PAI.md) — Source-level PAI module map
- **Root Bridge**: [../../../PAI.md](../../../PAI.md) — Authoritative PAI system bridge doc
- **Siblings**: [README.md](README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md) | [API_SPECIFICATION.md](API_SPECIFICATION.md)
