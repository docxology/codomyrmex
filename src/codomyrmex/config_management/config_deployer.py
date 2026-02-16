"""Backward-compatible shim -- delegates to config_management.deployment.config_deployer."""

from .deployment.config_deployer import (  # noqa: F401
    ConfigDeployment,
    ConfigurationDeployer,
    DeploymentStatus,
    Environment,
    EnvironmentType,
    deploy_configuration,
)
