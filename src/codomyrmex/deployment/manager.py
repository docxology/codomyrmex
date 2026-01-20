"""Deployment manager implementation."""

from .strategies import DeploymentStrategy
import logging

logger = logging.getLogger(__name__)

class DeploymentManager:
    """Orchestrates deployments using various strategies."""
    
    def deploy(self, service_name: str, version: str, strategy: DeploymentStrategy):
        """Execute a deployment."""
        logger.info(f"Initiating deployment of {service_name}:{version}")
        try:
            strategy.execute(service_name, version)
            logger.info(f"Successfully deployed {service_name}:{version}")
            return True
        except Exception as e:
            logger.error(f"Deployment failed for {service_name}:{version}: {e}")
            return False
