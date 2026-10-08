# Configuration Management - API Specification

## Introduction

This API specification documents the programmatic interfaces for the Configuration Management module of Codomyrmex. The module provides comprehensive configuration management, validation, and deployment capabilities for the Codomyrmex ecosystem, supporting multiple configuration sources, validation schemas, and secure secret management.

## Functions

### Function: `load_configuration(name: str, sources: list[str] | None = None, schema_path: str | None = None, defaults: dict[str, Any] | None = None) -> Configuration`

- **Description**: Load a named configuration with a new `ConfigurationManager`, deep-merging `defaults`, each readable source in order, and `<NAME>_*` environment variables (highest precedence; `__` nests keys), then resolving `${VAR}` and `${VAR:-default}` substitutions.
- **Parameters**:
  - `name`: Configuration name. Also used for the default sources and the environment-variable prefix.
  - `sources`: Files to load, in increasing precedence. Defaults to `<name>.yaml`, `<name>.yml`, `<name>.json` and the same names under `environments/<environment>/`.
  - `schema_path`: Path to a JSON schema; when it exists the configuration is validated against it (errors are logged, not raised).
  - `defaults`: Default values with the lowest precedence.
- **Return Value**: The loaded `Configuration`.
- **Errors**: Raises `FileNotFoundError` when a single explicit source was requested and nothing was found.

### Function: `validate_configuration(config: Configuration) -> list[str]`

- **Description**: Validate a `Configuration` against its schema (`Configuration.validate()`).
- **Parameters**:
  - `config`: Configuration to validate.
- **Return Value**: List of validation error messages; empty when the configuration is valid.

### Function: `manage_secrets(operation: str, **kwargs) -> Any`

- **Description**: Run one secret operation with a new `SecretManager`. Available when `SECRET_MANAGEMENT_AVAILABLE` is true.
- **Parameters**:
  - `operation`: One of `"store"`, `"get"`, `"get_by_name"`, `"list"`, `"delete"` or `"rotate"`.
  - `**kwargs`: Operation arguments: `name`, `value` and optional `metadata` for `store`; `secret_id` for `get` and `delete`; `name` for `get_by_name`.
- **Return Value**: The result of the matching `SecretManager` method (`store_secret()`, `get_secret()`, `get_secret_by_name()`, `list_secrets()`, `delete_secret()` or `rotate_key()`).
- **Errors**: Raises `CodomyrmexError` for an unknown operation.

### Function: `deploy_configuration(environment_name: str, config_files: list[str], deployed_by: str = "system") -> ConfigDeployment`

- **Description**: Deploy configuration files to a registered environment with a new `ConfigurationDeployer`.
- **Parameters**:
  - `environment_name`: Name of the target environment registered with the deployer.
  - `config_files`: Configuration files to deploy.
  - `deployed_by`: Who is deploying, recorded on the deployment.
- **Return Value**: The `ConfigDeployment` record.
- **Errors**: Raises `CodomyrmexError` when the environment is not registered.

### Function: `monitor_config_changes(config_paths: list[str | Path], workspace_dir: str | Path | None = None) -> dict[str, Any]`

- **Description**: Check configuration files once for changes with a `ConfigurationMonitor` and summarize the result.
- **Parameters**:
  - `config_paths`: Configuration files to check.
  - `workspace_dir`: Directory under which the monitor keeps `config_monitoring/` state (default: current directory).
- **Return Value**:

    ```python
    {
        "paths_monitored": <int>,
        "changes_detected": <int>,
        "summary": {
            "total_snapshots": <int>,
            "total_changes": <int>,
            "recent_changes": <int>,
            "total_audits": <int>,
            "last_audit_at": <ISO-8601 timestamp or None>,
            "status": "active"
        }
    }
    ```

### Method: `ConfigurationMonitor.audit_configuration(environment: str, config_dir: str | Path, compliance_rules: dict[str, Any] | None = None) -> ConfigAudit`

- **Description**: Audit the configuration files in a directory for an environment. There is no module-level `audit_configuration()` function; create a `ConfigurationMonitor` and call this method.
- **Parameters**:
  - `environment`: Environment name recorded on the audit.
  - `config_dir`: Directory whose configuration files are audited.
  - `compliance_rules`: Optional compliance rules.
- **Return Value**: The `ConfigAudit` record, also kept in `ConfigurationMonitor.get_audit_history()`.

## Data Structures

### Configuration

Represents a loaded and validated configuration:

```python
{
    "data": {<configuration_data>},
    "metadata": {
        "sources": [<list_of_source_files>],
        "environment": <str>,
        "loaded_at": <timestamp>,
        "validated": <bool>,
        "schema_version": <str>
    },
    "overrides": {<runtime_overrides>},
    "secrets": {<encrypted_secret_references>}
}
```

### ConfigSchema

JSON schema definition for configuration validation:

```python
{
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "properties": {<schema_properties>},
    "required": [<list_of_required_fields>],
    "additionalProperties": <bool>,
    "metadata": {
        "version": <str>,
        "description": <str>,
        "created_by": <str>
    }
}
```

### ConfigDeployment

Tracks configuration deployment status and history:

```python
{
    "id": <str>,
    "config_id": <str>,
    "target": <str>,
    "strategy": <str>,
    "status": "pending|in_progress|completed|failed|rolled_back",
    "start_time": <timestamp>,
    "end_time": <timestamp>,
    "backup_path": <str>,
    "rollback_available": <bool>,
    "validation_results": {<deployment_validation>},
    "error_message": <str>
}
```

### ConfigAudit

Results of configuration audit and compliance checking:

```python
{
    "config_id": <str>,
    "audit_timestamp": <timestamp>,
    "overall_score": <float>,
    "compliance_status": "compliant|non_compliant|warning",
    "findings": [
        {
            "rule": <str>,
            "severity": "critical|high|medium|low|info",
            "message": <str>,
            "path": <str>,
            "recommendation": <str>
        }
    ],
    "categories": {
        "security": <score>,
        "performance": <score>,
        "maintainability": <score>,
        "compliance": <score>
    }
}
```

### SecretManager

Manages encrypted secrets and credentials:

```python
{
    "backend": <str>,  # vault, aws_secretsmanager, azure_keyvault, etc.
    "encryption_method": <str>,
    "rotation_policy": {<rotation_rules>},
    "access_policies": [<list_of_access_policies>],
    "audit_log": [<list_of_secret_access_events>]
}
```

## Error Handling

- **Loading**: `load_configuration()` raises `FileNotFoundError` when a single explicit source is missing. Schema violations are logged and returned by `validate_configuration()`; they are not raised.
- **Secrets and deployment**: `manage_secrets()` and `deploy_configuration()` raise `codomyrmex.exceptions.CodomyrmexError` for an unknown operation or environment.

## Integration Patterns

### With Environment Setup

```python
from codomyrmex.config_management import load_configuration
from codomyrmex.environment_setup import validate_environment

# Validate the runtime environment before loading configuration
env_report = validate_environment(min_python="3.11")
if not env_report.valid:
    raise RuntimeError(f"Environment incomplete: {env_report.missing_items}")

# Load environment-specific configuration: config/app.yaml merged with
# config/environments/$ENVIRONMENT/app.yaml and APP_* environment variables
config = load_configuration("app")
```

### With Security Audit

```python
from codomyrmex.config_management import ConfigurationMonitor
from codomyrmex.security.digital import scan_secrets

# Audit configuration files for compliance issues
monitor = ConfigurationMonitor()
config_audit = monitor.audit_configuration("production", "config/")
print(config_audit.compliance_status, config_audit.issues_found)

# Follow up with secret scanning
secret_findings = scan_secrets("config/")
```

### With Project Orchestration

```python
from codomyrmex.config_management import deploy_configuration
from codomyrmex.logistics.orchestration.project import execute_workflow

# Deploy configuration as part of workflow
result = execute_workflow("config_deployment", {
    "config_management": {
        "config_path": "config/production.yaml",
        "target": "production_cluster",
        "strategy": "blue_green"
    }
})
```

## Security Considerations

- **Secret Encryption**: All secrets are encrypted at rest and in transit
- **Access Control**: Configuration access is controlled by roles and permissions
- **Audit Logging**: All configuration changes are logged for compliance
- **Validation**: Strict validation prevents injection and configuration attacks
- **Backup Security**: Configuration backups are encrypted and access-controlled
- **Key Rotation**: Automatic rotation of encryption keys for long-term security

## Performance Characteristics

- **Lazy Loading**: Configurations are loaded on-demand to reduce startup time
- **Caching**: Validated configurations are cached for performance
- **Efficient Validation**: Schema validation is optimized for large configurations
- **Monitoring Overhead**: Minimal performance impact from configuration monitoring
- **Secret Retrieval**: Efficient secret caching with automatic refresh

## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../../../docs/README.md)
- **Home**: [Root README](../../../README.md)
