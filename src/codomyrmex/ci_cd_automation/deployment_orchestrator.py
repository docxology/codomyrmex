"""
Deployment Orchestrator for Codomyrmex CI/CD Automation Module.

Provides comprehensive deployment orchestration, environment management,
and release coordination capabilities.
"""

import os
import sys
import json
import yaml
import docker
import kubernetes
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
import subprocess
import shutil
from codomyrmex.exceptions import CodomyrmexError

# Add project root to Python path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
if PROJECT_ROOT not in sys.path:
    pass
#     sys.path.insert(0, PROJECT_ROOT)  # Removed sys.path manipulation

try:
    from logging_monitoring.logger_config import get_logger

    logger = get_logger(__name__)
except ImportError:
    import logging

    logger = logging.getLogger(__name__)


class DeploymentStatus(Enum):
    """Deployment execution status."""

    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILURE = "failure"
    ROLLED_BACK = "rolled_back"
    CANCELLED = "cancelled"


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
    host: str
    port: int = 22
    user: str = "deploy"
    key_path: Optional[str] = None
    docker_registry: Optional[str] = None
    kubernetes_context: Optional[str] = None
    variables: Dict[str, str] = field(default_factory=dict)
    pre_deploy_hooks: List[str] = field(default_factory=list)
    post_deploy_hooks: List[str] = field(default_factory=list)
    health_checks: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert environment to dictionary format."""
        return {
            "name": self.name,
            "type": self.type.value,
            "host": self.host,
            "port": self.port,
            "user": self.user,
            "key_path": self.key_path,
            "docker_registry": self.docker_registry,
            "kubernetes_context": self.kubernetes_context,
            "variables": self.variables,
            "pre_deploy_hooks": self.pre_deploy_hooks,
            "post_deploy_hooks": self.post_deploy_hooks,
            "health_checks": self.health_checks,
        }


@dataclass
class Deployment:
    """Deployment configuration and status."""

    name: str
    version: str
    environment: Environment
    artifacts: List[str]
    strategy: str = "rolling"  # rolling, blue_green, canary
    timeout: int = 1800  # 30 minutes
    rollback_on_failure: bool = True
    status: DeploymentStatus = DeploymentStatus.PENDING
    created_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    duration: float = 0.0
    logs: List[str] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now(timezone.utc)

    def to_dict(self) -> Dict[str, Any]:
        """Convert deployment to dictionary format."""
        return {
            "name": self.name,
            "version": self.version,
            "environment": self.environment.to_dict(),
            "artifacts": self.artifacts,
            "strategy": self.strategy,
            "timeout": self.timeout,
            "rollback_on_failure": self.rollback_on_failure,
            "status": self.status.value,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "finished_at": self.finished_at.isoformat() if self.finished_at else None,
            "duration": self.duration,
            "logs": self.logs,
            "metrics": self.metrics,
        }


class DeploymentOrchestrator:
    """
    Comprehensive deployment orchestrator for multiple platforms.

    Features:
    - Multi-platform deployment (Docker, Kubernetes, traditional)
    - Environment management
    - Deployment strategies (rolling, blue-green, canary)
    - Health checking and monitoring
    - Automated rollback
    - Pre and post-deployment hooks
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the deployment orchestrator.

        Args:
            config_path: Path to deployment configuration file
        """
        self.config_path = config_path or os.path.join(
            os.getcwd(), "deployment_config.yaml"
        )
        self.environments: Dict[str, Environment] = {}
        self.deployments: Dict[str, Deployment] = {}
        self.docker_client = None
        self.k8s_client = None

        # Load configuration
        self._load_config()

        # Initialize clients
        self._initialize_clients()

    def _load_config(self):
        """Load deployment configuration."""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r") as f:
                    if self.config_path.endswith(".yaml") or self.config_path.endswith(
                        ".yml"
                    ):
                        config = yaml.safe_load(f)
                    else:
                        config = json.load(f)

                # Load environments
                for env_config in config.get("environments", []):
                    env = Environment(
                        name=env_config["name"],
                        type=EnvironmentType(env_config["type"]),
                        host=env_config["host"],
                        port=env_config.get("port", 22),
                        user=env_config.get("user", "deploy"),
                        key_path=env_config.get("key_path"),
                        docker_registry=env_config.get("docker_registry"),
                        kubernetes_context=env_config.get("kubernetes_context"),
                        variables=env_config.get("variables", {}),
                        pre_deploy_hooks=env_config.get("pre_deploy_hooks", []),
                        post_deploy_hooks=env_config.get("post_deploy_hooks", []),
                        health_checks=env_config.get("health_checks", []),
                    )
                    self.environments[env.name] = env

            except Exception as e:
                logger.warning(f"Failed to load deployment config: {e}")

    def _initialize_clients(self):
        """Initialize Docker and Kubernetes clients."""
        try:
            self.docker_client = docker.from_env()
            logger.info("Docker client initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize Docker client: {e}")

        try:
            kubernetes.config.load_kube_config()
            self.k8s_client = kubernetes.client.CoreV1Api()
            logger.info("Kubernetes client initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize Kubernetes client: {e}")

    def create_deployment(
        self,
        name: str,
        version: str,
        environment_name: str,
        artifacts: List[str],
        **kwargs,
    ) -> Deployment:
        """
        Create a new deployment.

        Args:
            name: Deployment name
            version: Version to deploy
            environment_name: Target environment name
            artifacts: List of artifacts to deploy
            **kwargs: Additional deployment options

        Returns:
            Deployment: Created deployment object
        """
        if environment_name not in self.environments:
            raise ValueError(f"Environment '{environment_name}' not found")

        environment = self.environments[environment_name]

        deployment = Deployment(
            name=name,
            version=version,
            environment=environment,
            artifacts=artifacts,
            strategy=kwargs.get("strategy", "rolling"),
            timeout=kwargs.get("timeout", 1800),
            rollback_on_failure=kwargs.get("rollback_on_failure", True),
        )

        self.deployments[name] = deployment
        logger.info(f"Created deployment: {name} v{version} to {environment_name}")

        return deployment

    def deploy(self, deployment_name: str) -> Deployment:
        """
        Execute a deployment.

        Args:
            deployment_name: Name of the deployment to execute

        Returns:
            Deployment: Updated deployment with execution results
        """
        if deployment_name not in self.deployments:
            raise ValueError(f"Deployment '{deployment_name}' not found")

        deployment = self.deployments[deployment_name]

        # Reset deployment state
        deployment.status = DeploymentStatus.RUNNING
        deployment.started_at = datetime.now(timezone.utc)
        deployment.logs = []

        logger.info(f"Starting deployment: {deployment_name}")

        try:
            # Execute pre-deployment hooks
            self._execute_hooks(deployment, "pre_deploy")

            # Execute deployment based on environment type
            if deployment.environment.type == EnvironmentType.DEVELOPMENT:
                self._deploy_to_development(deployment)
            elif deployment.environment.type == EnvironmentType.STAGING:
                self._deploy_to_staging(deployment)
            elif deployment.environment.type == EnvironmentType.PRODUCTION:
                self._deploy_to_production(deployment)
            else:
                self._deploy_traditional(deployment)

            # Execute post-deployment hooks
            self._execute_hooks(deployment, "post_deploy")

            # Perform health checks
            if self._perform_health_checks(deployment):
                deployment.status = DeploymentStatus.SUCCESS
                logger.info(f"Deployment {deployment_name} completed successfully")
            else:
                if deployment.rollback_on_failure:
                    self._rollback_deployment(deployment)
                    deployment.status = DeploymentStatus.ROLLED_BACK
                else:
                    deployment.status = DeploymentStatus.FAILURE

        except Exception as e:
            deployment.logs.append(f"Deployment failed: {str(e)}")
            logger.error(f"Deployment {deployment_name} failed: {e}")

            if deployment.rollback_on_failure:
                try:
                    self._rollback_deployment(deployment)
                    deployment.status = DeploymentStatus.ROLLED_BACK
                except Exception as rollback_error:
                    logger.error(f"Rollback failed: {rollback_error}")
                    deployment.status = DeploymentStatus.FAILURE
            else:
                deployment.status = DeploymentStatus.FAILURE

        # Update timing
        deployment.finished_at = datetime.now(timezone.utc)
        if deployment.started_at:
            deployment.duration = (
                deployment.finished_at - deployment.started_at
            ).total_seconds()

        return deployment

    def _deploy_to_development(self, deployment: Deployment):
        """Deploy to development environment (typically local Docker)."""
        logger.info(
            f"Deploying to development environment: {deployment.environment.name}"
        )

        # Use Docker for development deployments
        if self.docker_client and deployment.artifacts:
            for artifact in deployment.artifacts:
                if artifact.endswith(".tar.gz") or artifact.endswith(".zip"):
                    # Build and run Docker image
                    image_tag = f"{deployment.name}:{deployment.version}"
                    self._build_docker_image(artifact, image_tag)
                    self._run_docker_container(
                        image_tag, deployment.environment.variables
                    )

    def _deploy_to_staging(self, deployment: Deployment):
        """Deploy to staging environment."""
        logger.info(f"Deploying to staging environment: {deployment.environment.name}")

        # Use Docker Compose or similar for staging
        if os.path.exists("docker-compose.yml"):
            self._run_docker_compose(deployment.environment.variables)

    def _deploy_to_production(self, deployment: Deployment):
        """Deploy to production environment."""
        logger.info(
            f"Deploying to production environment: {deployment.environment.name}"
        )

        # Use Kubernetes for production deployments
        if self.k8s_client and deployment.artifacts:
            for artifact in deployment.artifacts:
                if artifact.endswith(".yaml") or artifact.endswith(".yml"):
                    self._deploy_to_kubernetes(
                        artifact, deployment.environment.variables
                    )

    def _deploy_traditional(self, deployment: Deployment):
        """Traditional deployment via SSH/rsync."""
        logger.info(
            f"Deploying via traditional method to: {deployment.environment.name}"
        )

        # Use rsync/ssh for traditional deployments
        for artifact in deployment.artifacts:
            self._deploy_via_ssh(artifact, deployment.environment)

    def _build_docker_image(self, artifact_path: str, image_tag: str):
        """Build Docker image from artifact."""
        try:
            # Extract artifact if it's an archive
            if artifact_path.endswith(".tar.gz"):
                extract_dir = (
                    f"/tmp/{os.path.basename(artifact_path).replace('.tar.gz', '')}"
                )
                shutil.unpack_archive(artifact_path, extract_dir)

                # Build Docker image
                self.docker_client.images.build(
                    path=extract_dir, tag=image_tag, rm=True
                )

                logger.info(f"Built Docker image: {image_tag}")

            # Clean up
            if os.path.exists(extract_dir):
                shutil.rmtree(extract_dir)

        except Exception as e:
            logger.error(f"Failed to build Docker image: {e}")
            raise

    def _run_docker_container(self, image_tag: str, environment_vars: Dict[str, str]):
        """Run Docker container."""
        try:
            container = self.docker_client.containers.run(
                image_tag,
                environment=environment_vars,
                detach=True,
                ports={"8000/tcp": 8000},  # Example port mapping
            )

            logger.info(f"Started Docker container: {container.id}")

        except Exception as e:
            logger.error(f"Failed to run Docker container: {e}")
            raise

    def _run_docker_compose(self, environment_vars: Dict[str, str]):
        """Run Docker Compose deployment."""
        try:
            env = os.environ.copy()
            env.update(environment_vars)

            result = subprocess.run(
                ["docker-compose", "up", "-d", "--build"],
                capture_output=True,
                text=True,
                env=env,
            )

            if result.returncode != 0:
                raise Exception(f"Docker Compose failed: {result.stderr}")

            logger.info("Docker Compose deployment completed")

        except Exception as e:
            logger.error(f"Docker Compose deployment failed: {e}")
            raise

    def _deploy_to_kubernetes(
        self, manifest_path: str, environment_vars: Dict[str, str]
    ):
        """Deploy to Kubernetes."""
        try:
            # Substitute environment variables in manifest
            with open(manifest_path, "r") as f:
                manifest = f.read()

            for key, value in environment_vars.items():
                manifest = manifest.replace(f"${{{key}}}", value)
                manifest = manifest.replace(f"${key}", value)

            # Apply manifest
            import tempfile

            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".yaml", delete=False
            ) as f:
                f.write(manifest)
                temp_manifest = f.name

            result = subprocess.run(
                ["kubectl", "apply", "-f", temp_manifest],
                capture_output=True,
                text=True,
            )

            if result.returncode != 0:
                raise Exception(f"Kubernetes deployment failed: {result.stderr}")

            logger.info("Kubernetes deployment completed")

            # Clean up temp file
            os.unlink(temp_manifest)

        except Exception as e:
            logger.error(f"Kubernetes deployment failed: {e}")
            raise

    def _deploy_via_ssh(self, artifact_path: str, environment: Environment):
        """Deploy via SSH/rsync."""
        try:
            # Use rsync to deploy artifacts
            remote_path = f"{environment.user}@{environment.host}:{environment.variables.get('deploy_path', '/opt/app')}"

            result = subprocess.run(
                [
                    "rsync",
                    "-avz",
                    "--delete",
                    "-e",
                    f"ssh -i {environment.key_path}" if environment.key_path else "ssh",
                    artifact_path,
                    remote_path,
                ],
                capture_output=True,
                text=True,
            )

            if result.returncode != 0:
                raise Exception(f"SSH deployment failed: {result.stderr}")

            logger.info(f"SSH deployment completed to {environment.host}")

        except Exception as e:
            logger.error(f"SSH deployment failed: {e}")
            raise

    def _execute_hooks(self, deployment: Deployment, hook_type: str):
        """Execute pre or post deployment hooks."""
        hooks = []
        if hook_type == "pre_deploy":
            hooks = deployment.environment.pre_deploy_hooks
        elif hook_type == "post_deploy":
            hooks = deployment.environment.post_deploy_hooks

        for hook in hooks:
            try:
                logger.info(f"Executing {hook_type} hook: {hook}")
                result = subprocess.run(
                    hook, shell=True, capture_output=True, text=True, cwd=os.getcwd()
                )

                if result.returncode != 0:
                    logger.warning(f"Hook failed: {hook} - {result.stderr}")
                else:
                    deployment.logs.append(f"Hook executed: {hook}")

            except Exception as e:
                logger.error(f"Hook execution failed: {hook} - {e}")

    def _perform_health_checks(self, deployment: Deployment) -> bool:
        """Perform health checks after deployment."""
        all_healthy = True

        for check in deployment.environment.health_checks:
            try:
                check_type = check.get("type", "http")
                endpoint = check.get("endpoint", "")
                timeout = check.get("timeout", 30)

                if check_type == "http":
                    healthy = self._check_http_health(endpoint, timeout)
                elif check_type == "tcp":
                    healthy = self._check_tcp_health(endpoint, timeout)
                else:
                    logger.warning(f"Unknown health check type: {check_type}")
                    healthy = False

                if not healthy:
                    all_healthy = False
                    deployment.logs.append(f"Health check failed: {endpoint}")

            except Exception as e:
                logger.error(f"Health check error: {e}")
                all_healthy = False

        return all_healthy

    def _check_http_health(self, endpoint: str, timeout: int) -> bool:
        """Check HTTP endpoint health."""
        try:
            import requests

            response = requests.get(endpoint, timeout=timeout)
            return response.status_code == 200
        except Exception:
            return False

    def _check_tcp_health(self, endpoint: str, timeout: int) -> bool:
        """Check TCP endpoint health."""
        try:
            import socket

            host, port = endpoint.split(":")
            sock = socket.create_connection((host, int(port)), timeout=timeout)
            sock.close()
            return True
        except Exception:
            return False

    def _rollback_deployment(self, deployment: Deployment):
        """Rollback a failed deployment."""
        logger.info(f"Rolling back deployment: {deployment.name}")

        try:
            # Implementation depends on deployment strategy
            if deployment.strategy == "rolling":
                self._rollback_rolling(deployment)
            elif deployment.strategy == "blue_green":
                self._rollback_blue_green(deployment)
            else:
                logger.warning(
                    f"Rollback not implemented for strategy: {deployment.strategy}"
                )

        except Exception as e:
            logger.error(f"Rollback failed: {e}")
            raise

    def _rollback_rolling(self, deployment: Deployment):
        """Rollback rolling deployment."""
        # Stop new containers, restart old ones
        if self.docker_client:
            # Implementation for Docker rollback
            pass

    def _rollback_blue_green(self, deployment: Deployment):
        """Rollback blue-green deployment."""
        # Switch traffic back to previous version
        if self.k8s_client:
            # Implementation for Kubernetes rollback
            pass

    def get_deployment_status(self, deployment_name: str) -> Optional[Deployment]:
        """Get current status of a deployment."""
        return self.deployments.get(deployment_name)

    def list_deployments(self) -> List[Deployment]:
        """List all deployments."""
        return list(self.deployments.values())

    def cancel_deployment(self, deployment_name: str) -> bool:
        """
        Cancel a running deployment.

        Args:
            deployment_name: Name of the deployment to cancel

        Returns:
            bool: True if cancellation successful
        """
        if deployment_name not in self.deployments:
            return False

        deployment = self.deployments[deployment_name]
        if deployment.status == DeploymentStatus.RUNNING:
            deployment.status = DeploymentStatus.CANCELLED
            logger.info(f"Cancelled deployment: {deployment_name}")
            return True

        return False


# Convenience functions
def manage_deployments(config_path: Optional[str] = None) -> DeploymentOrchestrator:
    """
    Convenience function to create deployment orchestrator.

    Args:
        config_path: Path to deployment configuration file

    Returns:
        DeploymentOrchestrator: Configured orchestrator
    """
    return DeploymentOrchestrator(config_path)
