# Agent Guidelines - Config Management

**Version**: v1.0.5 | **Status**: Active | **Last Updated**: March 2026

## Module Overview

Configuration loading, validation, and environment management.

## Key Classes

- **ConfigLoader** — Load from YAML/JSON/env
- **ConfigValidator** — Validate configurations
- **Environment** — Environment-specific configs
- **SecretManager** — Secure secret handling

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

| PAI Agent | Access Level | Primary Capabilities | Trust Level |
|-----------|-------------|---------------------|-------------|
| **Engineer** | Full | `get_config`, `set_config`, `validate_config`; full config CRUD | TRUSTED |
| **Architect** | Read + Design | `get_config`, `validate_config`; config schema review, settings architecture | OBSERVED |
| **QATester** | Validation | `validate_config`, `get_config`; config correctness and schema compliance | OBSERVED |

### Engineer Agent
**Use Cases**: Reading/writing config during BUILD and EXECUTE, validating configuration files, applying environment-specific overrides.

### Architect Agent
**Use Cases**: Config schema design, reviewing configuration hierarchies, validating settings architecture.

### QATester Agent
**Use Cases**: Validating config files during VERIFY, checking schema compliance, confirming config values match expectations.

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)
