# Configuration Inheritance Example

## Overview

This example demonstrates advanced configuration patterns using inheritance, overrides, and conditional configuration. It shows how to create maintainable configuration hierarchies that work across different environments and use cases.

## Key Concepts

### 1. Basic Inheritance

```yaml
# Base configuration
base:
  app:
    name: "Codomyrmex"
    version: "1.0.0"

# Environment-specific override
development:
  extends: base  # Inherit from base
  app:
    debug: true  # Override/add settings
```

### 2. Multiple Levels of Inheritance

```yaml
base:           # Level 1
  logging:
    level: INFO

staging:        # Level 2 - extends base
  extends: base
  logging:
    file: staging.log

api_service:    # Level 3 - extends staging
  extends: staging
  api:
    rate_limit: 1000
```

### 3. Conditional Configuration

```yaml
conditional_config:
  development:
    when: "${ENV} == 'development'"
    config:
      debug: true

  production:
    when: "${ENV} == 'production'"
    config:
      debug: false
```

## Environment Examples

### Development Environment

**Inherits from**: `base`
**Purpose**: Local development with debugging enabled

```yaml
development:
  extends: base
  logging:
    level: DEBUG        # More verbose logging
    file: logs/dev.log  # Development log file

  features:
    hot_reload: true    # Enable hot reloading
    debug_toolbar: true # Enable debug tools
    experimental: true  # Allow experimental features
```

### Staging Environment

**Inherits from**: `base`
**Purpose**: Pre-production testing environment

```yaml
staging:
  extends: base
  logging:
    level: INFO         # Production-like logging
    file: logs/staging.log

  database:
    type: postgresql    # Real database
    host: staging-db.example.com

  features:
    experimental: false # No experimental features
    monitoring: true    # Enable monitoring
```

### Production Environment

**Inherits from**: `base`
**Purpose**: Live production environment

```yaml
production:
  extends: base
  logging:
    level: WARNING      # Minimal logging
    file: logs/prod.log

  database:
    type: postgresql
    ssl_enabled: true   # Security enabled

  features:
    monitoring: true
    auto_scaling: true  # Production features
```

## Service-Specific Configuration

### API Service

```yaml
api_service:
  extends: production   # Inherit production settings

  api:
    rate_limit: 1000    # API-specific settings
    cors_enabled: true

  features:
    api_gateway: true   # Service-specific features
```

### Worker Service

```yaml
worker_service:
  extends: production

  performance:
    memory_limit: 2GB   # Higher memory for workers
    cpu_limit: 80

  features:
    background_jobs: true
    queue_processing: true
```

## Configuration Merging

### Shallow Merge

```yaml
base:
  a: 1
  b: 2

override:
  b: 20  # Override existing value
  c: 30  # Add new value

result:
  a: 1   # Preserved from base
  b: 20  # Overridden
  c: 30  # Added
```

### Deep Merge

```yaml
base:
  database:
    host: localhost
    credentials:
      username: user
      password: pass

override:
  database:
    credentials:
      password: new_pass  # Deep override

result:
  database:
    host: localhost      # Preserved
    credentials:
      username: user     # Preserved
      password: new_pass # Overridden
```

## Feature Flag Inheritance

```yaml
base_flags:
  core_features: true
  logging: true
  monitoring: false

dev_flags:
  extends: base_flags
  monitoring: true      # Override
  experimental: true    # Add
  debug_features: true  # Add

prod_flags:
  extends: base_flags
  monitoring: true      # Override
  performance_optimization: true  # Add
```

## Usage Examples

### Loading Inherited Configuration

```python
from examples._common.config_loader import load_config

def load_environment_config(env: str) -> dict:
    """Load configuration for specific environment."""

    # Load base configuration
    base_config = load_config("environment_base.yaml")

    # Load environment-specific configuration
    env_config = load_config(f"environment_{env}.yaml")

    # Merge configurations (implementation would handle 'extends' key)
    return merge_configs(base_config, env_config)

# Usage
dev_config = load_environment_config("dev")
prod_config = load_environment_config("prod")
```

### Conditional Configuration Loading

```python
import os

def load_conditional_config() -> dict:
    """Load configuration based on conditions."""

    env = os.environ.get("ENV", "development")

    # Load base config
    config = load_config("config_base.yaml")

    # Apply conditional overrides
    if env == "development":
        dev_overrides = load_config("config_dev_overrides.yaml")
        config = merge_configs(config, dev_overrides)
    elif env == "production":
        prod_overrides = load_config("config_prod_overrides.yaml")
        config = merge_configs(config, prod_overrides)

    return config
```

## Best Practices

### 1. Configuration Hierarchy

```
base_config.yaml          # Shared settings
├── environment_dev.yaml  # Development overrides
├── environment_staging.yaml  # Staging overrides
└── environment_prod.yaml # Production overrides
```

### 2. Naming Conventions

- `base` - Base configuration
- `development`/`dev` - Development environment
- `staging` - Staging environment
- `production`/`prod` - Production environment
- `{service}_service` - Service-specific configuration

### 3. Environment Variables

```yaml
# Use environment variables for sensitive/secrets
database:
  password: "${DB_PASSWORD}"
  host: "${DB_HOST:localhost}"
```

### 4. Validation

```python
def validate_config(config: dict) -> bool:
    """Validate configuration structure."""

    # Required sections
    required = ["logging", "database"]
    for section in required:
        if section not in config:
            raise ValueError(f"Missing required section: {section}")

    # Environment-specific validation
    env = config.get("environment", "development")
    if env == "production":
        if not config.get("security", {}).get("ssl_enabled"):
            raise ValueError("SSL must be enabled in production")

    return True
```

## Common Patterns

### Database Configuration Inheritance

```yaml
database_base:
  connection_pool:
    min_connections: 1
    max_connections: 10
    timeout: 30

database_dev:
  extends: database_base
  type: sqlite
  database: dev.db

database_prod:
  extends: database_base
  type: postgresql
  host: "${DB_HOST}"
  ssl_enabled: true
  connection_pool:
    min_connections: 5
    max_connections: 50
```

### API Configuration Inheritance

```yaml
api_base:
  timeout: 30
  retries: 3

api_dev:
  extends: api_base
  debug: true
  port: 8000

api_prod:
  extends: api_base
  debug: false
  port: 443
  rate_limit: 1000
```

### Logging Configuration Inheritance

```yaml
logging_base:
  format: "%(asctime)s - %(levelname)s - %(message)s"
  max_file_size: 10485760

logging_dev:
  extends: logging_base
  level: DEBUG
  file: logs/dev.log

logging_prod:
  extends: logging_base
  level: WARNING
  file: logs/prod.log
  handlers:
    - file
    - syslog
```

## Implementation Notes

### Configuration Loader

To implement inheritance, you would need a configuration loader that:

1. Loads the base configuration
2. Recursively loads extended configurations
3. Merges configurations with proper override semantics
4. Handles environment variable substitution
5. Validates the final configuration

### Merge Strategies

- **Shallow merge**: Only top-level keys are merged
- **Deep merge**: Nested dictionaries are merged recursively
- **Override**: Later configurations completely replace earlier ones
- **Append**: Arrays are concatenated, not replaced

### Error Handling

```python
def load_inherited_config(config_path: str) -> dict:
    """Load configuration with inheritance support."""

    try:
        config = load_config(config_path)

        # Check for extends
        if "extends" in config:
            base_config = load_inherited_config(config["extends"])
            config = merge_configs(base_config, config)
            del config["extends"]  # Remove extends key

        return config

    except FileNotFoundError:
        raise ConfigError(f"Configuration file not found: {config_path}")
    except yaml.YAMLError as e:
        raise ConfigError(f"Invalid YAML in {config_path}: {e}")
```

---

**Status**: Example Configuration
**Last Updated**: January 2026
**Compatibility**: Any configuration loader with inheritance support
