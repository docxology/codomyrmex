# Agent Guidelines - Environment Setup

**Version**: v1.1.9 | **Status**: Active | **Last Updated**: March 2026

## Module Overview

Environment validation, dependency checking, and setup automation. This module is the baseline for all other module execution environments. It validates Python version requirements, detects and integrates with the `uv` package manager, loads `.env` files for credential management, checks API key availability, and resolves dependency conflicts using pip introspection. The `DependencyResolver` provides full audit capabilities including conflict detection, pyproject.toml validation, outdated package discovery, and virtual environment detection.

## Key Files

| File | Purpose |
|------|---------|
| `__init__.py` | Exports `validate_environment`, `check_dependencies`, `install_dependencies`, `DependencyResolver`, `ValidationReport`, `DependencyStatus`, `APIKeyReport`, `DependencyInfo`, `Conflict`, and all utility functions |
| `env_checker.py` | `ValidationReport`, `DependencyStatus`, `APIKeyReport` dataclasses; `validate_environment()`, `check_dependencies()`, `check_and_setup_env_vars()`, `check_api_keys()`, `is_uv_available()`, `generate_environment_report()` |
| `dependency_resolver.py` | `DependencyResolver` class: conflict detection via `pip check`, `list_installed()`, `suggest_resolution()`, `validate_pyproject()`, `detect_virtualenv()`, `find_outdated()`, `full_audit()`, `generate_report()` |
| `mcp_tools.py` | MCP tools: `env_check`, `env_list_deps` |

## Key Classes

- **ValidationReport** -- Dataclass with `valid: bool` and `missing_items: List[str]`. Returned by `validate_environment()`.
- **DependencyStatus** -- Dataclass with `name: str` and `installed: bool`. Returned by `check_dependencies()`.
- **APIKeyReport** -- Dataclass with `all_present: bool` and `missing: List[str]`. Returned by `check_api_keys()`.
- **DependencyInfo** -- Dataclass with `name`, `version`, `required_by`, `requires`. Returned by `DependencyResolver.list_installed()`.
- **Conflict** -- Dataclass with `package`, `installed_version`, `required_version`, `required_by`, `severity`. Returned by `DependencyResolver.check_conflicts()`.
- **DependencyResolver** -- Full dependency analysis: `check_conflicts()`, `list_installed()`, `suggest_resolution()`, `validate_pyproject()`, `detect_virtualenv()`, `find_outdated()`, `full_audit()`, `generate_report()`.

## MCP Tools Available

| Tool | Description | Trust Level |
|------|-------------|-------------|
| `env_check` | Check Python version validity, uv availability, and uv-managed environment status. Returns dict of boolean checks. | SAFE |
| `env_list_deps` | Verify all required Python dependencies are installed. Returns True if all satisfied, or a detail dict. | SAFE |

## Agent Instructions

1. **Verify first** -- Run `validate_environment()` before performing task operations.
2. **Setup Credentials** -- Use `check_and_setup_env_vars()` at start to ensure API keys are loaded from `.env`.
3. **Handle Missing** -- If `ValidationReport.valid` is False, use `install_dependencies()` to resolve package gaps.
4. **Leverage uv** -- Always prefer `uv` tools via `get_uv_path()` for any environment mutations.
5. **Detailed Reporting** -- Use `generate_environment_report()` for logging or debugging session startup.
6. **Audit before releases** -- Use `DependencyResolver.full_audit()` to detect conflicts and unpinned dependencies before deployment.
7. **Detect virtualenv** -- Call `DependencyResolver.detect_virtualenv()` to confirm isolated execution context before installing packages.

## Operating Contracts

- `validate_environment()` must be called before any module initialization in production workflows; it is the gate for all downstream operations.
- `check_and_setup_env_vars()` loads `.env` via `python-dotenv` and returns a list of missing required variables; an empty list means all present.
- `install_dependencies()` prefers `uv pip install` when `uv` is available; falls back to `pip install` otherwise.
- `DependencyResolver.check_conflicts()` shells out to `pip check` with a 30-second timeout; returns an empty list on timeout or missing pip.
- `DependencyResolver.validate_pyproject()` flags unpinned dependencies (missing `>=`, `==`, or `~=` version specifiers).
- **DO NOT** mutate the system PATH or system Python environment in production -- use uv virtual environments only.
- **DO NOT** install dependencies without first checking if they already exist via `check_dependencies()` or `ensure_dependencies_installed()`.
- **DO NOT** hard-code Python version requirements; use `validate_environment(min_python=...)` parameter.
- `DependencyResolver` requires internet access for `find_outdated()` and `list_installed()` operations; use `@pytest.mark.network` for tests that call these.

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

### Dependency Audit

```python
from codomyrmex.environment_setup import DependencyResolver
from pathlib import Path

resolver = DependencyResolver()
audit = resolver.full_audit(pyproject_path=Path("pyproject.toml"))

if audit["conflict_count"] > 0:
    for suggestion in audit["suggestions"]:
        print(f"Fix: {suggestion}")
```

## Testing Patterns

```python
# Zero-mock system check
from codomyrmex.environment_setup import is_uv_available
# Always check real system state
assert isinstance(is_uv_available(), bool)
```

## PAI Agent Role Access Matrix

| PAI Agent | Access Level | MCP Tools | Trust Level |
|-----------|-------------|-----------|-------------|
| **Engineer** | Full | `env_check`, `env_list_deps` | TRUSTED |
| **Architect** | Read + Design | `env_check`, `env_list_deps` -- dependency inventory, environment specification review | OBSERVED |
| **QATester** | Validation | `env_check`, `env_list_deps` -- environment health verification, dependency availability testing | OBSERVED |
| **Researcher** | Read-only | `env_check` -- check environment state before research operations | SAFE |

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


## Rule Reference

This module is governed by the following rule file:

- [`src/codomyrmex/agentic_memory/rules/modules/environment_setup.cursorrules`](src/codomyrmex/agentic_memory/rules/modules/environment_setup.cursorrules)
