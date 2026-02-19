# DEPRECATED(v0.2.0): Shim module. Import from config_management.deployment.config_deployer instead. Will be removed in v0.3.0.
"""Backward-compatible shim -- delegates to config_management.deployment.config_deployer."""

from .deployment.config_deployer import (  # noqa: F401
    ConfigDeployment,
    ConfigurationDeployer,
    DeploymentStatus,
    Environment,
    EnvironmentType,
    deploy_configuration,
)
