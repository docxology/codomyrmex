# Environment Setup Tutorials

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Tutorials for configuring and validating development environments.

## Available Tutorials

| Tutorial | Description |
|----------|-------------|
| [Basic Validation](#basic-validation) | Validate environment requirements |
| [Dependency Check](#dependency-check) | Verify installed dependencies |
| [Auto Setup](#auto-setup) | Automated environment setup |

## Basic Validation

```python
from codomyrmex.environment_setup import validate_environment

# Validate all requirements
result = validate_environment()

if result.valid:
    print("✓ Environment ready")
else:
    for issue in result.issues:
        print(f"✗ {issue}")
```

## Dependency Check

```python
from codomyrmex.environment_setup import check_dependencies

deps = check_dependencies(["python", "git", "ollama"])

for dep in deps:
    status = "✓" if dep.installed else "✗"
    print(f"{status} {dep.name}: {dep.version or 'not found'}")
```

## Auto Setup

```python
from codomyrmex.environment_setup import auto_setup

# Automatically install missing dependencies
result = auto_setup()
print(f"Installed: {result.installed}")
print(f"Skipped: {result.skipped}")
```

## Navigation

- **Parent**: [Environment Setup Documentation](../README.md)
- **Source**: [src/codomyrmex/environment_setup/](../../../../src/codomyrmex/environment_setup/)
