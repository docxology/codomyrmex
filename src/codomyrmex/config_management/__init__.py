"""
Configuration Management Module for Codomyrmex.

The Configuration Management module provides configuration management,
validation, and deployment capabilities for the Codomyrmex ecosystem.

Integration:
- Uses `logging_monitoring` for all logging (ensure `setup_logging()` is called in your main app).
- Integrates with `security` for secure configuration handling.
- Works with `environment_setup` for environment-specific configurations.
- Supports `static_analysis` for configuration validation.

Available functions:
- load_configuration: Load and merge configuration from multiple sources
- validate_configuration: Validate configuration against schemas
- manage_secrets: Secure secret management and rotation
- deploy_configuration: Deploy configuration to target environments
- monitor_config_changes: Track configuration changes and drift
- generate_config_docs: Generate configuration documentation
- backup_configuration: Backup and restore configurations
- audit_configuration: Audit configuration compliance and security

Data structures:
- Configuration: Configuration object with validation and metadata
- ConfigSchema: JSON schema for configuration validation
- SecretManager: Secure secret storage and retrieval
- ConfigDeployment: Configuration deployment tracking
- ConfigAudit: Configuration audit and compliance results
"""

# Shared schemas for cross-module interop
import contextlib

with contextlib.suppress(ImportError):
    from codomyrmex.validation.schemas import Result, ResultStatus

from codomyrmex.config_monitoring import (
    ConfigAudit,
    ConfigurationMonitor,
    ConfigWatcher,
    monitor_config_changes,
)

from .core import (
    ConfigSchema,
    Configuration,
    ConfigurationManager,
    load_configuration,
    validate_configuration,
)
from .deployment import (
    ConfigDeployment,
    ConfigurationDeployer,
    deploy_configuration,
)

# Import secret management conditionally (requires cryptography)
try:
    from .secrets import (
        SecretManager,
        encrypt_configuration,
        manage_secrets,
    )

    SECRET_MANAGEMENT_AVAILABLE = True
except ImportError:
    # cryptography not available
    SECRET_MANAGEMENT_AVAILABLE = False


def cli_commands():
    """Return CLI commands for the config_management module."""

    def _show(**kwargs):
        """Show current configuration."""
        mgr = ConfigurationManager()
        config = mgr.get_current()
        print("=== Current Configuration ===")
        for key, value in (config or {}).items():
            print(f"  {key}: {value}")

    def _validate(**kwargs):
        """Validate configuration against schemas."""
        mgr = ConfigurationManager()
        result = mgr.validate()
        status = "VALID" if result else "INVALID"
        print(f"Configuration status: {status}")
        if hasattr(result, "errors") and result.errors:
            for err in result.errors:
                print(f"  ERROR: {err}")

    return {
        "show": {"handler": _show, "help": "Show current configuration"},
        "validate": {
            "handler": _validate,
            "help": "Validate configuration against schemas",
        },
    }


from typing import Any


def get_config(key: str, default: Any = None, namespace: str = "default") -> Any:
    """Retrieve a configuration value by key.

    Args:
        key: Configuration key to look up (e.g., 'database.host').
        default: Default value if the key is not found.
        namespace: Configuration namespace. Defaults to 'default'.

    Returns:
        The configuration value.
    """
    manager = ConfigurationManager()
    config = manager.get_configuration(namespace)
    if not config:
        config = manager.load_configuration(namespace)
    return config.get_value(key, default)


def set_config(key: str, value: Any, namespace: str = "default") -> None:
    """set a configuration value.

    Args:
        key: Configuration key to set.
        value: Value to store.
        namespace: Configuration namespace. Defaults to 'default'.
    """
    manager = ConfigurationManager()
    config = manager.get_configuration(namespace)
    if not config:
        config = manager.load_configuration(namespace)
    config.set_value(key, value)
    manager.save_configuration(namespace, f"{manager.config_dir}/{namespace}.yaml")


def validate_config(namespace: str = "default") -> dict[str, Any]:
    """Validate configuration consistency and completeness.

    Args:
        namespace: Configuration namespace to validate.

    Returns:
        Validation report dictionary containing valid status and issues.
    """
    manager = ConfigurationManager()
    config = manager.get_configuration(namespace)
    if not config:
        config = manager.load_configuration(namespace)

    errors = config.validate()
    return {
        "valid": len(errors) == 0,
        "issues": errors,
    }


# Build __all__ dynamically based on available components
__all__ = [
    "ConfigAudit",
    "ConfigDeployment",
    "ConfigSchema",
    "ConfigWatcher",
    "Configuration",
    # Configuration deployment
    "ConfigurationDeployer",
    "ConfigurationManager",
    # Configuration monitoring
    "ConfigurationMonitor",
    "cli_commands",
    "deploy_configuration",
    # Configuration management
    "get_config",
    "load_configuration",
    "monitor_config_changes",
    "set_config",
    "validate_config",
    "validate_configuration",
]

# Add secret management if available
if SECRET_MANAGEMENT_AVAILABLE:
    __all__.extend(
        [
            "SecretManager",
            "encrypt_configuration",
            "manage_secrets",
        ]
    )
