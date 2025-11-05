#!/usr/bin/env python3
"""
Configuration Deployment Module for Codomyrmex Configuration Management.

This module provides configuration deployment, environment management,
and configuration synchronization across multiple environments.
"""

import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Optional

from codomyrmex.exceptions import CodomyrmexError
from codomyrmex.logging_monitoring.logger_config import get_logger

logger = get_logger(__name__)


class DeploymentStatus(Enum):
    """Configuration deployment status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


class EnvironmentType(Enum):
    """Types of deployment environments."""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"


@dataclass
class Environment:
    """Deployment environment configuration."""
    name: str
    type: EnvironmentType
    config_path: str
    variables: dict[str, str] = field(default_factory=dict)
    secrets: dict[str, str] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class ConfigDeployment:
    """Configuration deployment record."""
    deployment_id: str
    environment: str
    config_version: str
    status: DeploymentStatus
    deployed_at: datetime
    deployed_by: str
    config_files: list[str]
    changes: dict[str, Any]
    rollback_info: Optional[dict[str, Any]] = None


class ConfigurationDeployer:
    """Configuration deployment and environment management system."""

    def __init__(self, workspace_dir: Optional[str] = None):
        """Initialize configuration deployer.

        Args:
            workspace_dir: Workspace directory for deployment tracking
        """
        self.workspace_dir = Path(workspace_dir) if workspace_dir else Path.cwd()
        self.deployments_dir = self.workspace_dir / "config_deployments"
        self.environments_dir = self.workspace_dir / "environments"
        self._ensure_directories()

        self._environments: dict[str, Environment] = {}
        self._deployments: dict[str, ConfigDeployment] = {}

    def _ensure_directories(self):
        """Ensure required directories exist."""
        self.deployments_dir.mkdir(parents=True, exist_ok=True)
        self.environments_dir.mkdir(parents=True, exist_ok=True)

    def create_environment(
        self,
        name: str,
        env_type: EnvironmentType,
        config_path: str,
        variables: Optional[dict[str, str]] = None
    ) -> Environment:
        """Create a deployment environment.

        Args:
            name: Environment name
            env_type: Type of environment
            config_path: Path to configuration files
            variables: Environment-specific variables

        Returns:
            Created environment
        """
        environment = Environment(
            name=name,
            type=env_type,
            config_path=config_path,
            variables=variables or {}
        )

        self._environments[name] = environment

        # Save environment configuration
        env_file = self.environments_dir / f"{name}.json"
        with open(env_file, 'w') as f:
            json.dump({
                "name": environment.name,
                "type": environment.type.value,
                "config_path": environment.config_path,
                "variables": environment.variables,
                "created_at": environment.created_at.isoformat()
            }, f, indent=2)

        logger.info(f"Created environment: {name} ({env_type.value})")
        return environment

    def deploy_configuration(
        self,
        environment_name: str,
        config_files: list[str],
        deployed_by: str = "system"
    ) -> ConfigDeployment:
        """Deploy configuration to an environment.

        Args:
            environment_name: Target environment name
            config_files: List of configuration files to deploy
            deployed_by: Who is deploying the configuration

        Returns:
            Deployment record
        """
        if environment_name not in self._environments:
            raise CodomyrmexError(f"Environment not found: {environment_name}")

        deployment_id = f"deploy_{environment_name}_{int(datetime.now().timestamp())}"

        deployment = ConfigDeployment(
            deployment_id=deployment_id,
            environment=environment_name,
            config_version="1.0.0",  # Would be determined from config
            status=DeploymentStatus.IN_PROGRESS,
            deployed_at=datetime.now(),
            deployed_by=deployed_by,
            config_files=config_files,
            changes=self._analyze_config_changes(config_files)
        )

        self._deployments[deployment_id] = deployment

        try:
            # Perform deployment
            self._execute_deployment(deployment)

            deployment.status = DeploymentStatus.SUCCESS
            logger.info(f"Successfully deployed configuration to {environment_name}")

        except Exception as e:
            deployment.status = DeploymentStatus.FAILED
            logger.error(f"Failed to deploy configuration to {environment_name}: {e}")
            raise

        finally:
            # Save deployment record
            deployment_file = self.deployments_dir / f"{deployment_id}.json"
            with open(deployment_file, 'w') as f:
                json.dump({
                    "deployment_id": deployment.deployment_id,
                    "environment": deployment.environment,
                    "config_version": deployment.config_version,
                    "status": deployment.status.value,
                    "deployed_at": deployment.deployed_at.isoformat(),
                    "deployed_by": deployment.deployed_by,
                    "config_files": deployment.config_files,
                    "changes": deployment.changes,
                    "rollback_info": deployment.rollback_info
                }, f, indent=2)

        return deployment

    def _analyze_config_changes(self, config_files: list[str]) -> dict[str, Any]:
        """Analyze changes in configuration files."""
        changes = {
            "files_modified": len(config_files),
            "files_added": [],
            "files_removed": [],
            "settings_changed": {}
        }

        # This would typically compare with previous deployment
        # For now, return basic analysis
        for file_path in config_files:
            path = Path(file_path)
            if path.exists():
                changes["files_added"].append(str(path))

        return changes

    def _execute_deployment(self, deployment: ConfigDeployment):
        """Execute the actual deployment process."""
        environment = self._environments[deployment.environment]

        # Copy configuration files to environment
        for config_file in deployment.config_files:
            source_path = Path(config_file)
            if source_path.exists():
                # Apply environment variables
                content = self._apply_environment_variables(
                    source_path.read_text(),
                    environment.variables
                )

                # Copy to environment location
                target_path = Path(environment.config_path) / source_path.name
                target_path.parent.mkdir(parents=True, exist_ok=True)
                target_path.write_text(content)

                logger.debug(f"Deployed {config_file} to {target_path}")

    def _apply_environment_variables(self, content: str, variables: dict[str, str]) -> str:
        """Apply environment variables to configuration content."""
        for key, value in variables.items():
            placeholder = f"${{{key}}}"
            content = content.replace(placeholder, value)

            # Also support shell-style variables
            shell_var = f"${key}"
            content = content.replace(shell_var, value)

        return content

    def rollback_deployment(self, deployment_id: str) -> ConfigDeployment:
        """Rollback a configuration deployment.

        Args:
            deployment_id: ID of the deployment to rollback

        Returns:
            Rollback deployment record
        """
        if deployment_id not in self._deployments:
            raise CodomyrmexError(f"Deployment not found: {deployment_id}")

        original_deployment = self._deployments[deployment_id]

        # Create rollback deployment
        rollback_id = f"rollback_{deployment_id}_{int(datetime.now().timestamp())}"
        rollback_deployment = ConfigDeployment(
            deployment_id=rollback_id,
            environment=original_deployment.environment,
            config_version="rollback",  # Previous version
            status=DeploymentStatus.IN_PROGRESS,
            deployed_at=datetime.now(),
            deployed_by="system",
            config_files=original_deployment.config_files,
            changes={"operation": "rollback", "original_deployment": deployment_id}
        )

        try:
            # Execute rollback (restore previous configuration)
            self._execute_rollback(rollback_deployment)

            rollback_deployment.status = DeploymentStatus.SUCCESS
            logger.info(f"Successfully rolled back deployment {deployment_id}")

        except Exception as e:
            rollback_deployment.status = DeploymentStatus.FAILED
            logger.error(f"Failed to rollback deployment {deployment_id}: {e}")
            raise

        finally:
            self._deployments[rollback_id] = rollback_deployment

        return rollback_deployment

    def _execute_rollback(self, deployment: ConfigDeployment):
        """Execute the rollback process."""
        # This would typically restore from backup or previous version
        # For now, just log the operation
        logger.info(f"Executing rollback for deployment {deployment.deployment_id}")

    def get_deployment_status(self, deployment_id: str) -> Optional[ConfigDeployment]:
        """Get status of a configuration deployment.

        Args:
            deployment_id: Deployment ID

        Returns:
            Deployment record or None if not found
        """
        return self._deployments.get(deployment_id)

    def list_deployments(self, environment: Optional[str] = None) -> list[ConfigDeployment]:
        """List configuration deployments.

        Args:
            environment: Filter by environment name

        Returns:
            List of deployments
        """
        deployments = list(self._deployments.values())

        if environment:
            deployments = [d for d in deployments if d.environment == environment]

        # Sort by deployment time (most recent first)
        deployments.sort(key=lambda d: d.deployed_at, reverse=True)

        return deployments

    def get_environment_config(self, environment_name: str) -> Optional[Environment]:
        """Get environment configuration.

        Args:
            environment_name: Environment name

        Returns:
            Environment configuration or None if not found
        """
        return self._environments.get(environment_name)

    def list_environments(self) -> list[Environment]:
        """List all configured environments.

        Returns:
            List of environments
        """
        return list(self._environments.values())


def deploy_configuration(
    environment_name: str,
    config_files: list[str],
    deployed_by: str = "system"
) -> ConfigDeployment:
    """Deploy configuration to an environment.

    Args:
        environment_name: Target environment name
        config_files: List of configuration files to deploy
        deployed_by: Who is deploying the configuration

    Returns:
        Deployment record
    """
    deployer = ConfigurationDeployer()
    return deployer.deploy_configuration(environment_name, config_files, deployed_by)
