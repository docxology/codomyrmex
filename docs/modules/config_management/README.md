# Config Management Module Documentation

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Hierarchical configuration management with environment-aware overrides, validation, and hot-reloading.


## Installation

```bash
uv pip install codomyrmex
```

## Key Features

- **DeploymentStatus** — Configuration deployment status.
- **EnvironmentType** — Types of deployment environments.
- **Environment** — Deployment environment configuration.
- **ConfigDeployment** — Configuration deployment record.
- **ConfigurationDeployer** — Configuration deployment and environment management system.
- **ConfigSchema** — JSON schema for configuration validation.
- `deploy_configuration()` — Deploy configuration to an environment.
- `load_configuration()` — Convenience function to load configuration.
- `validate_configuration()` — Convenience function to validate configuration.
- `create_logging_migration_rules()` — Create migration rules for logging configuration.

## Quick Start

```python
from codomyrmex.config_management import DeploymentStatus, EnvironmentType, Environment

instance = DeploymentStatus()
```

## Source Files

- `config_deployer.py`
- `config_loader.py`
- `config_migrator.py`
- `config_monitor.py`
- `config_validator.py`
- `secret_manager.py`
- `watcher.py`

## Directory Contents

| File | Description |
|------|-------------|
| `README.md` | This documentation |
| `AGENTS.md` | Agent coordination guide |
| `SPEC.md` | Technical specification |


## Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k config_management -v
```

## Navigation

- **Source**: [src/codomyrmex/config_management/](../../../src/codomyrmex/config_management/)
- **Parent**: [Modules](../README.md)
