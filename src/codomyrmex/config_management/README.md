# config_management

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Configuration management module providing loading, validation, deployment, monitoring, and secret management for the Codomyrmex platform. Supports merging configuration from multiple sources (files, environment variables, defaults), JSON Schema-based validation, deployment tracking to target environments, real-time file watching for configuration changes, and optional encrypted secret management via the `cryptography` library. Integrates with `logging_monitoring`, `security`, and `environment_setup` modules.

## Key Exports

### Configuration Loading and Validation
- **`ConfigurationManager`** -- Central manager that loads, merges, validates, and provides access to configuration from multiple sources
- **`load_configuration()`** -- Convenience function to load and merge configuration from file paths, environment, and defaults
- **`validate_configuration()`** -- Validates a configuration object against a schema, returning errors and warnings
- **`Configuration`** -- Configuration data object with metadata, validation state, and source tracking
- **`ConfigSchema`** -- JSON Schema definition for validating configuration structure and values

### Configuration Deployment
- **`ConfigurationDeployer`** -- Deploys configuration to target environments with rollback support
- **`deploy_configuration()`** -- Convenience function to deploy a configuration to a named environment
- **`ConfigDeployment`** -- Tracks a deployment event with timestamp, environment, status, and diff

### Configuration Monitoring
- **`ConfigurationMonitor`** -- Monitors configuration for changes, drift, and compliance violations
- **`monitor_config_changes()`** -- Convenience function to start monitoring a configuration source
- **`ConfigAudit`** -- Audit result containing compliance checks, drift detection, and security findings
- **`ConfigWatcher`** -- File-system watcher that triggers callbacks when configuration files change

### Secret Management (optional, requires `cryptography`)
- **`SecretManager`** -- Encrypted secret storage and retrieval with key rotation support
- **`manage_secrets()`** -- Convenience function for secret CRUD operations
- **`encrypt_configuration()`** -- Encrypts sensitive fields within a configuration object

## Directory Contents

- `config_loader.py` -- ConfigurationManager, Configuration, ConfigSchema, load/validate functions
- `config_deployer.py` -- ConfigurationDeployer, ConfigDeployment, deploy function
- `config_monitor.py` -- ConfigurationMonitor, ConfigAudit, change monitoring
- `config_validator.py` -- Additional validation logic and schema enforcement
- `config_migrator.py` -- Configuration migration between schema versions
- `secret_manager.py` -- SecretManager and encryption utilities (optional `cryptography` dependency)
- `watcher.py` -- ConfigWatcher for file-system change detection

## Quick Start

```python
from codomyrmex.config_management import DeploymentStatus, EnvironmentType

# Create a DeploymentStatus instance
deploymentstatus = DeploymentStatus()

# Use EnvironmentType for additional functionality
environmenttype = EnvironmentType()
```


## Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k config_management -v
```

## Navigation

- **Full Documentation**: [docs/modules/config_management/](../../../docs/modules/config_management/)
- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: ../../../README.md
