# Environment Setup Configuration

**Version**: v1.1.4 | **Status**: Active | **Last Updated**: March 2026

## Overview

Environment validation, dependency checking, and uv package manager integration. Validates Python version, virtual environments, API keys, and installed dependencies.

## Quick Configuration

```bash
export VIRTUAL_ENV=""    # Path to active virtual environment (auto-detected) (required)
export UV_ACTIVE="1"    # Indicator that uv environment is active
export CONDA_DEFAULT_ENV=""    # Active Conda environment name (required)
```

## Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `VIRTUAL_ENV` | str | None | Path to active virtual environment (auto-detected) |
| `UV_ACTIVE` | str | `1` | Indicator that uv environment is active |
| `CONDA_DEFAULT_ENV` | str | None | Active Conda environment name |

## PAI Integration

PAI agents interact with environment_setup through direct Python imports. Environment validation runs automatically on import. API key checks use a configurable list of required keys per module.

## Validation

```bash
# Verify module is available
codomyrmex modules | grep environment_setup

# Run module health check
codomyrmex status
```

## Navigation

- [Source Module](../../src/codomyrmex/environment_setup/README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md)
