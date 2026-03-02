# Agent Guidelines - Environment Setup

**Version**: v1.1.0 | **Status**: Active | **Last Updated**: March 2026

## Module Overview

Environment validation, dependency checking, and setup automation. This module is the baseline for all other module execution environments.

## Key Functions

### Core Validation
- **`validate_environment(min_python)`** — Aggregated status check of system requirements. Returns `ValidationReport`.
- **`check_dependencies(list)`** — Detailed check for specific installed packages. Returns `List[DependencyStatus]`.
- **`ensure_dependencies_installed(list)`** — Logs status of dependencies, returns True if all exist.
- **`install_dependencies(source)`** — Automates dependency installation via `uv` (preferred) or `pip`.

### Environment Management
- **`check_and_setup_env_vars(repo_root, required, optional)`** — Load `.env` and verify key presence.
- **`check_api_keys(keys)`** — Focused check for credential availability. Returns `APIKeyReport`.

### System Info
- **`is_uv_available()`** — Boolean for `uv` existence.
- **`get_uv_path()`** — String path to `uv` executable.
- **`is_uv_environment()`** — Boolean for current execution context being uv-based.
- **`generate_environment_report()`** — String summary of system state.

## Agent Instructions

1. **Verify first** — Run `validate_environment()` before performing task operations.
2. **Setup Credentials** — Use `check_and_setup_env_vars()` at start to ensure API keys are loaded from `.env`.
3. **Handle Missing** — If `ValidationReport.valid` is False, use `install_dependencies()` to resolve package gaps.
4. **Leverage uv** — Always prefer `uv` tools via `get_uv_path()` for any environment mutations.
5. **Detailed Reporting** — Use `generate_environment_report()` for logging or debugging session startup.

## Common Patterns

```python
from codomyrmex.environment_setup import (
    validate_environment, check_and_setup_env_vars, install_dependencies
)

# Load environment and validate
missing_vars = check_and_setup_env_vars(required=["OPENAI_API_KEY"])
report = validate_environment()

if not report.valid or missing_vars:
    print(f"Environment Gap: {report.missing_items}, Missing Vars: {missing_vars}")
    # Fix if possible
    if "python-dotenv" in report.missing_items:
        install_dependencies("pyproject.toml")
```

## Testing Patterns

```python
# Zero-mock system check
from codomyrmex.environment_setup import is_uv_available
# Always check real system state
assert isinstance(is_uv_available(), bool)
```

## MCP Tools Available

| Tool | Description | Trust Level |
|------|-------------|-------------|
| `env_check` | Check Python version validity, uv availability, and uv-managed environment status. Returns dict of boolean checks. | SAFE |
| `env_list_deps` | Verify all required Python dependencies are installed. Returns True if all satisfied, or a detail dict. | SAFE |

## Operating Contracts

**DO:**
- Call `validate_environment()` at session start before any heavy operations
- Use `check_and_setup_env_vars(required=[...])` to load `.env` and verify API keys
- Prefer `uv` via `get_uv_path()` for any package installation operations
- Check `is_uv_environment()` before assuming fast package operations

**DO NOT:**
- Install dependencies without first checking if they already exist
- Mutate the system Python environment — use uv virtual environments only
- Hard-code Python version requirements; use `validate_environment(min_python=...)` parameter

## PAI Agent Role Access Matrix

| PAI Agent | Access Level | Primary Capabilities | Trust Level |
|-----------|-------------|---------------------|-------------|
| **Engineer** | Full | Environment validation, dependency checking, setup automation; `env_check`, `env_list_deps` | TRUSTED |
| **Architect** | Read + Design | Dependency inventory, environment specification review | OBSERVED |
| **QATester** | Validation | Environment health verification, dependency availability testing | OBSERVED |
| **Researcher** | Read-only | Check environment state via `env_check` before research operations | SAFE |

### Engineer Agent
**Use Cases**: Setting up execution environments during BUILD, validating dependencies before EXECUTE, automating environment configuration.

### Architect Agent
**Use Cases**: Reviewing required dependencies, auditing environment specifications, planning dependency upgrades.

### QATester Agent
**Use Cases**: Verifying all required dependencies are available, testing environment isolation, confirming setup completeness during VERIFY.

### Researcher Agent
**Use Cases**: Confirm environment prerequisites before long research operations, check uv availability.

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)
