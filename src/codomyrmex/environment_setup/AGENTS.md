# Agent Guidelines - Environment Setup

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Module Overview

Environment validation, dependency checking, and setup automation.

## Key Classes

- **validate_environment()** — Check system requirements
- **check_dependencies()** — Verify installed packages
- **install_dependencies(source)** — Install from requirements
- **get_uv_path()** — Get uv package manager path

## Agent Instructions

1. **Validate first** — Call `validate_environment()` before running
2. **Check API keys** — Verify required keys are set
3. **Use uv** — Prefer uv over pip for faster installs
4. **Cache results** — Environment rarely changes
5. **Report missing** — List all missing deps, not just first

## Common Patterns

```python
from codomyrmex.environment_setup import (
    validate_environment, check_dependencies, install_dependencies
)

# Full environment validation
report = validate_environment()
if not report.valid:
    print(f"Missing: {report.missing_items}")
    install_dependencies("pyproject.toml")

# Check specific dependencies
deps = check_dependencies(["numpy", "pandas", "openai"])
for dep in deps:
    if not dep.installed:
        print(f"Install {dep.name}: uv pip install {dep.name}")

# Verify API keys
from codomyrmex.environment_setup import check_api_keys
keys = check_api_keys(["OPENAI_API_KEY", "ANTHROPIC_API_KEY"])
if not keys.all_present:
    print(f"Missing: {keys.missing}")
```

## Testing Patterns

```python
# Verify environment check
report = validate_environment()
assert hasattr(report, "valid")
assert hasattr(report, "missing_items")

# Verify dependency check
deps = check_dependencies(["pip"])
assert len(deps) == 1
assert deps[0].installed  # pip should exist
```

## PAI Agent Role Access Matrix

| PAI Agent | Access Level | Primary Capabilities | Trust Level |
|-----------|-------------|---------------------|-------------|
| **Engineer** | Full | Environment validation, dependency checking, setup automation; full configuration control | TRUSTED |
| **Architect** | Read + Design | Dependency inventory, environment specification review | OBSERVED |
| **QATester** | Validation | Environment health verification, dependency availability testing | OBSERVED |

### Engineer Agent
**Use Cases**: Setting up execution environments during BUILD, validating dependencies before EXECUTE, automating environment configuration.

### Architect Agent
**Use Cases**: Reviewing required dependencies, auditing environment specifications, planning dependency upgrades.

### QATester Agent
**Use Cases**: Verifying all required dependencies are available, testing environment isolation, confirming setup completeness during VERIFY.

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)
