# Environment Setup Module

**Version**: v1.1.9 | **Status**: Active | **Last Updated**: March 2026

The `environment_setup` module provides tools for validating the development environment, managing dependencies, and configuring environment variables.

## PAI Integration

| Algorithm Phase | Role | Tools Used |
|----------------|------|-----------|
| **OBSERVE** | Validate system dependencies before session start | `validate_environment()` |
| **VERIFY** | Run environment health checks after configuration changes | `generate_environment_report()` |
| **PLAN** | Check capability prerequisites before task execution | `check_dependencies(list)` |

PAI agents access this module to confirm all dependencies are present before delegating work. The Architect agent calls `validate_environment()` during OBSERVE phase.

## Key Exports

### Functions
- **`validate_environment(min_python)`** — Comprehensive validation of Python version and core packages.
- **`check_dependencies(list)`** — Detailed check for specified installed packages.
- **`ensure_dependencies_installed(list)`** — Logs status of dependencies, returns True if all exist.
- **`install_dependencies(source)`** — Trigger `uv` or `pip` to install packages from `pyproject.toml` or `requirements.txt`.
- **`check_and_setup_env_vars(repo_root, required, optional)`** — Load `.env` and verify required key presence.
- **`check_api_keys(keys)`** — specific check for credentials.
- **`is_uv_available()`** — Check if `uv` is in system PATH.
- **`get_uv_path()`** — Get path to `uv` executable.
- **`is_uv_environment()`** — Check if current environment is uv-managed.
- **`generate_environment_report()`** — Detailed report of system configuration.

## Quick Start

```python
from codomyrmex.environment_setup import (
    validate_environment,
    check_and_setup_env_vars,
    is_uv_available
)

# 1. Load env vars and check for required keys
missing = check_and_setup_env_vars(required=["OPENAI_API_KEY", "ANTHROPIC_API_KEY"])
if missing:
    print(f"Required API keys missing: {missing}")

# 2. Comprehensive system validation
report = validate_environment(min_python="3.11")
if not report.valid:
    print(f"Environment check failed: {report.missing_items}")

# 3. Quick check for uv
if is_uv_available():
    print("Fast package management enabled via uv.")
```

## Exports

| Category | Exports |
|----------|---------|
| **Validation** | `validate_environment`, `validate_python_version`, `validate_environment_completeness` |
| **Dependencies** | `check_dependencies`, `ensure_dependencies_installed`, `install_dependencies`, `DependencyResolver` |
| **Configuration** | `check_and_setup_env_vars`, `check_api_keys`, `APIKeyReport` |
| **System Info** | `is_uv_available`, `get_uv_path`, `is_uv_environment`, `generate_environment_report` |

## Directory Contents

```text
environment_setup/
├── __init__.py          # Exports all functions
├── env_checker.py       # validate_environment, check_dependencies, generate_environment_report
├── dependency_resolver.py  # DependencyResolver, install_dependencies
├── mcp_tools.py         # MCP tools: env_check, env_list_deps
└── scripts/             # Setup scripts
```

## Testing

```bash
uv run pytest src/codomyrmex/tests/unit/environment_setup/ -v
```

## Documentation

- [Functional Specification](SPEC.md)
- [Agent Guidelines](AGENTS.md)
- [Module USAGE](USAGE_EXAMPLES.md)

## Navigation

- [SPEC](SPEC.md) | [AGENTS](AGENTS.md) | [PAI](PAI.md)
