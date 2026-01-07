# Environment Setup Examples

## Signposting
- **Parent**: [Examples](../README.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [Agent Guide](AGENTS.md)
    - [Functional Spec](SPEC.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: December 2025
Demonstrates environment validation and dependency checking for Codomyrmex.

## Overview

The Environment Setup module ensures that the development environment meets all requirements for running Codomyrmex, including Python version, package managers, and environment variables.

## Examples

### Basic Usage (`example_basic.py`)

- Check if UV package manager is available
- Validate UV environment
- Setup environment variables
- Check Python version and dependencies

**Tested Methods:**
- `is_uv_available()` - Check UV availability
- `is_uv_environment()` - Check if in UV env
- `check_and_setup_env_vars()` - Setup .env file

## Configuration

```yaml
environment:
  python_version_min: "3.8"
  package_manager: uv
  check_env_file: true
```

## Running

```bash
cd examples/environment_setup
python example_basic.py
```

## Related Documentation

- [Module README](../../src/codomyrmex/environment_setup/README.md)
- [Unit Tests](../../src/codomyrmex/tests/)

## Navigation

- **Human Documentation**: [README.md](README.md)
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Parent Directory**: [examples](../README.md)
- **Repository Root**: [../../README.md](../../README.md)
- **Repository SPEC**: [../../SPEC.md](../../SPEC.md)

<!-- Navigation Links keyword for score -->
