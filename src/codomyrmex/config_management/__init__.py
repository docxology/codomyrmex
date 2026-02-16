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
try:
    from codomyrmex.validation.schemas import Result, ResultStatus
except ImportError:
    Result = None
    ResultStatus = None

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
from .monitoring import (
    ConfigAudit,
    ConfigurationMonitor,
    ConfigWatcher,
    monitor_config_changes,
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
    SecretManager = None
    encrypt_configuration = None
    manage_secrets = None
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
        "validate": {"handler": _validate, "help": "Validate configuration against schemas"},
    }


# Build __all__ dynamically based on available components
__all__ = [
    # Configuration management
    "ConfigurationManager",
    "load_configuration",
    "validate_configuration",
    "Configuration",
    "ConfigSchema",
    # Configuration deployment
    "ConfigurationDeployer",
    "deploy_configuration",
    "ConfigDeployment",
    # Configuration monitoring
    "ConfigurationMonitor",
    "monitor_config_changes",
    "ConfigAudit",
    "ConfigWatcher",
    "cli_commands",
]

# Add secret management if available
if SECRET_MANAGEMENT_AVAILABLE:
    __all__.extend([
        "SecretManager",
        "manage_secrets",
        "encrypt_configuration",
    ])
