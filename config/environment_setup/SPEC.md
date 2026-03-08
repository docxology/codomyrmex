# Environment Setup Configuration Specification

**Version**: v1.1.9 | **Status**: Active | **Last Updated**: March 2026

## Overview

Environment validation, dependency checking, and uv package manager integration. Validates Python version, virtual environments, API keys, and installed dependencies. This specification documents the configuration schema and constraints.

## Configuration Schema

| Key | Type | Required | Default | Description |
|-----|------|----------|---------|-------------|
| `VIRTUAL_ENV` | string | Yes | None | Path to active virtual environment (auto-detected) |
| `UV_ACTIVE` | string | No | `1` | Indicator that uv environment is active |
| `CONDA_DEFAULT_ENV` | string | Yes | None | Active Conda environment name |

## Environment Variables

```bash
# Required
export VIRTUAL_ENV=""    # Path to active virtual environment (auto-detected)
export CONDA_DEFAULT_ENV=""    # Active Conda environment name

# Optional (defaults shown)
export UV_ACTIVE="1"    # Indicator that uv environment is active
```

## Design Principles

- **Centralized Config**: All settings accessible via config_management module
- **Env-First**: Environment variables take precedence over config file values
- **Explicit Defaults**: All optional settings have documented defaults
- **Zero-Mock**: No placeholder or fake configuration values in production

## Constraints

- `VIRTUAL_ENV` must be set before module initialization
- `CONDA_DEFAULT_ENV` must be set before module initialization
- Configuration is validated on first use; invalid values raise explicit errors
- No silent fallback to placeholder values

## Dependencies

**Depends on**: `config_management`, `environment_setup`

## Navigation

- [README.md](README.md) | [AGENTS.md](AGENTS.md) | [Source Module](../../src/codomyrmex/environment_setup/SPEC.md)
