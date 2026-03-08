# Agent Guidelines - Config Management

**Version**: v1.1.9 | **Status**: Active | **Last Updated**: March 2026

## Module Overview

Hierarchical configuration management supporting YAML/JSON loading, namespace-scoped key access, schema validation, and environment-variable merging. Three MCP tools (`get_config`, `set_config`, `validate_config`) expose the full config lifecycle to PAI agents. Default values are centralized here and consumed by all 130 modules to avoid hard-coded strings.

## Key Files

| File | Purpose |
|------|---------|
| `__init__.py` | Exports `get_config`, `set_config`, `validate_config`, `ConfigManager` |
| `defaults.py` | Centralized default values (URLs, ports, connection strings) |
| `mcp_tools.py` | MCP tools: `get_config`, `set_config`, `validate_config` |

## MCP Tools Available

| Tool | Description | Trust Level |
|------|-------------|-------------|
| `get_config` | Retrieve a configuration value by key and namespace. | SAFE |
| `set_config` | Set a configuration value (persisted for session lifetime). | TRUSTED |
| `validate_config` | Validate a configuration dictionary against common patterns. | SAFE |

## Key Classes

- **`ConfigManager`** — Namespace-scoped configuration store with YAML/JSON loading
- **`get_config(key, namespace)`** — Function for key lookup with namespace support
- **`set_config(key, value, namespace)`** — Function for setting config values

## Agent Instructions

1. **Layer configs** — defaults → file → env → args
2. **Validate early** — Check config at startup
3. **No secrets in code** — Use SecretManager
4. **Document settings** — List all config options
5. **Type coercion** — Handle string→int conversion

## Common Patterns

```python
from codomyrmex.config_management import (
    ConfigLoader, Environment, SecretManager
)

# Load configuration
config = ConfigLoader.load(
    path="config.yaml",
    environment="production",
    env_prefix="MYAPP_"
)

# Access values
db_host = config.get("database.host")
debug = config.get("debug", default=False)

# Secrets
secrets = SecretManager()
api_key = secrets.get("API_KEY")

# Environment-aware
env = Environment.detect()
if env.is_production:
    log_level = "WARNING"
```

## Testing Patterns

```python
# Verify config loading
config = ConfigLoader.load("test_config.yaml")
assert config.get("key") is not None

# Verify environment detection
env = Environment.detect()
assert env.name in ["development", "production", "test"]

# Verify validation
errors = ConfigValidator.validate(config, schema)
assert len(errors) == 0
```

## PAI Agent Role Access Matrix

| PAI Agent | Access Level | MCP Tools | Trust Level |
|-----------|-------------|-----------|-------------|
| **Engineer** | Full | `get_config`, `set_config`, `validate_config` | TRUSTED |
| **Architect** | Read + Design | `get_config`, `validate_config` — schema review, settings architecture | OBSERVED |
| **QATester** | Validation | `validate_config`, `get_config` — config correctness and schema compliance | OBSERVED |
| **Researcher** | Read-only | `get_config` — read configuration state during analysis | SAFE |

### Engineer Agent
**Use Cases**: Reading/writing config during BUILD and EXECUTE, validating configuration files, applying environment-specific overrides.

### Architect Agent
**Use Cases**: Config schema design, reviewing configuration hierarchies, validating settings architecture.

### QATester Agent
**Use Cases**: Validating config files during VERIFY, checking schema compliance, confirming config values match expectations.

### Researcher Agent
**Use Cases**: Reading configuration state to understand system behavior during research analysis.

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)


## Rule Reference

This module is governed by the following rule file:

- [`src/codomyrmex/agentic_memory/rules/modules/config_management.cursorrules`](src/codomyrmex/agentic_memory/rules/modules/config_management.cursorrules)
