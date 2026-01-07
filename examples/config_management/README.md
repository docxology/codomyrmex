# Config Management Examples

## Signposting
- **Parent**: [Examples](../README.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [Agent Guide](AGENTS.md)
    - [Functional Spec](SPEC.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: December 2025
Demonstrates configuration loading, validation, and management using the Codomyrmex Config Management module.

## Overview

The Config Management module provides comprehensive configuration handling including multi-source loading, schema validation, migration support, and secure secret management.

## Examples

### Basic Usage (`example_basic.py`)

- Load configurations from multiple sources (YAML/JSON)
- Validate configurations against schemas
- Apply configuration migrations
- Access configuration values safely
- Merge configuration overrides

**Tested Methods:**
- `load_configuration()` - Load from multiple sources (from `test_config_management.py`)
- `validate_configuration()` - Schema validation (from `test_config_management.py`)
- `migrate_configuration()` - Version migration (from `test_config_management_enhanced.py`)

## Configuration

```yaml
config_management:
  config_sources: [config.yaml, config_overrides.yaml]
  schema:
    app: {required: true, type: object}
    database: {required: true, type: object}
  access_examples:
    - key: app.name
      default: "Unknown App"

app:
  name: Codomyrmex Config Example
  version: 1.0.0

database:
  host: localhost
  credentials:
    username: ${DB_USER:codomyrmex}
    password: ${DB_PASSWORD:secret123}
```

## Configuration Sources

- **config.yaml**: Main configuration file
- **config_overrides.yaml**: Environment-specific overrides
- **config.json**: Alternative JSON format
- **Environment Variables**: Dynamic value substitution

## Running

```bash
cd examples/config_management
python example_basic.py

# With custom database credentials
DB_USER=myuser DB_PASSWORD=mypass python example_basic.py
```

## Expected Output

The example will:
1. Load configurations from multiple sources
2. Merge configuration overrides
3. Validate against schema rules
4. Apply configuration migrations
5. Demonstrate safe value access
6. Generate configuration summary
7. Save detailed results to JSON file

## Configuration Features

- **Multi-Source Loading**: Files, environment variables, secrets
- **Schema Validation**: JSON Schema validation with custom rules
- **Migration Support**: Version-based configuration migration
- **Secret Management**: Secure handling of sensitive data
- **Environment Overrides**: Development/staging/production configs
- **Hot Reloading**: Configuration updates without restart

## Use Cases

- **Application Configuration**: Centralized app settings
- **Environment Management**: Dev/staging/prod configurations
- **Secret Management**: Secure credential handling
- **Feature Flags**: Runtime feature toggles
- **Service Discovery**: Dynamic service endpoints

## Integration with Other Modules

The config management module integrates with:
- **Logging**: Configuration-driven log levels and formats
- **Security Audit**: Validate security configurations
- **Containerization**: Container environment configs
- **Database Management**: Connection string management
- **API Standardization**: API configuration and versioning

## Related Documentation

- [Module README](../../src/codomyrmex/config_management/README.md)
- [Unit Tests](../../src/codomyrmex/tests/)
- [Enhanced Tests](../../src/codomyrmex/tests/)

## Navigation

- **Human Documentation**: [README.md](README.md)
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Parent Directory**: [examples](../README.md)
- **Repository Root**: [../../README.md](../../README.md)
- **Repository SPEC**: [../../SPEC.md](../../SPEC.md)

<!-- Navigation Links keyword for score -->
