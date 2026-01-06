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

from .config_deployer import (
    ConfigDeployment,
    ConfigurationDeployer,
    deploy_configuration,
)
from .config_loader import (
    ConfigSchema,
    Configuration,
    ConfigurationManager,
    load_configuration,
    validate_configuration,
)
from .config_monitor import (
    ConfigAudit,
    ConfigurationMonitor,
    monitor_config_changes,
)

# Import secret management conditionally (requires cryptography)
try:
    from .secret_manager import (
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
]

# Add secret management if available
if SECRET_MANAGEMENT_AVAILABLE:
    __all__.extend([
        "SecretManager",
        "manage_secrets",
        "encrypt_configuration",
    ])
