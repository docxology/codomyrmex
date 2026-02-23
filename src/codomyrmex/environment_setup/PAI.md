# Personal AI Infrastructure — Environment Setup Module

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The Environment Setup module validates the development environment, ensures dependency integrity, and creates a stable runtime for Codomyrmex agents. It acts as the **Gatekeeper** for the system, preventing execution in misconfigured environments. It is a **Foundation Layer** module.

## PAI Capabilities

### Comprehensive Validation

The primary entry point for agents to verify their runtime environment.

```python
from codomyrmex.environment_setup import validate_environment_completeness

# Single call to validate Python version, dependencies, and .env
if validate_environment_completeness():
    print("System ready for PAI execution")
else:
    print("Environment misconfigured - check logs")
    exit(1)
```

### Granular Checks

Individual checks for specific resource availablity.

```python
from codomyrmex.environment_setup import (
    validate_python_version,
    is_uv_available,
    ensure_dependencies_installed,
    check_and_setup_env_vars,
)

# 1. Check Runtime
if not validate_python_version():
    raise SystemError("Python 3.10+ required")

# 2. Check Tooling
if is_uv_available():
    print("Using 'uv' for fast package management")

# 3. Check Configuration
if not check_and_setup_env_vars("/path/to/repo_root"):
    print("Warning: .env file not found")
```

## Key Exports

| Export | Type | Purpose |
|--------|------|---------|
| `validate_environment_completeness` | Function | **Primary entry point**: Runs all checks |
| `ensure_dependencies_installed` | Function | Verifies `cased/kit` and `python-dotenv` |
| `check_and_setup_env_vars` | Function | Loads `.env` into `os.environ` |
| `validate_python_version` | Function | Enforces Python 3.10+ requirement |
| `is_uv_available` | Function | Detects `uv` package manager |

## PAI Algorithm Phase Mapping

| Phase | Environment Setup Contribution |
|-------|-------------------------------|
| **OBSERVE** | `validate_environment_completeness` — Initial system health check |
| **PLAN** | `is_uv_available` — Determine available tooling for build steps |
| **VERIFY** | `ensure_dependencies_installed` — Pre-flight check before complex operations |

## Architecture Role

**Foundation Layer** — Critical dependency for:

1. **CLI Entry Points** (fail fast if env is bad)
2. **Agent Initialization** (ensure config is loaded)
3. **Build Tools** (leverage `uv` if present)

## Navigation

- **Self**: [PAI.md](PAI.md)
- **Parent**: [../PAI.md](../PAI.md) — Source-level PAI module map
- **Root Bridge**: [../../../PAI.md](../../../PAI.md) — Authoritative PAI system bridge doc
- **Siblings**: [README.md](README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md)
