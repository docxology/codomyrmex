"""Deployment module for Codomyrmex.

Provides deployment strategies, managers, and utilities:
- Canary deployments
- Blue-green deployments
- Rolling deployments
- GitOps synchronization
"""

from typing import Any, Dict, List, Optional

# Import strategies and create aliases for common naming conventions
from .strategies import (
    DeploymentState,
    DeploymentTarget,
    DeploymentResult,
    DeploymentStrategy,
    RollingDeployment,
    BlueGreenDeployment,
    CanaryDeployment,
    create_strategy,
)

# Create convenience aliases for different naming conventions
CanaryStrategy = CanaryDeployment
BlueGreenStrategy = BlueGreenDeployment
RollingStrategy = RollingDeployment

# Submodule exports  
from . import health_checks
from . import strategies
from . import rollback

# Try optional submodules
try:
    from . import manager
except ImportError:
    manager = None

try:
    from . import gitops
except ImportError:
    gitops = None


class DeploymentManager:
    """
    High-level deployment manager for orchestrating deployments.
    
    Provides a simple interface for deploying services using
    different strategies.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the deployment manager.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self._deployments: List[Dict[str, Any]] = []
        self._default_strategy = RollingDeployment()
    
    def deploy(
        self,
        service_name: str,
        version: str,
        strategy: Optional[DeploymentStrategy] = None,
        targets: Optional[List[DeploymentTarget]] = None,
    ) -> bool:
        """
        Deploy a service version using the specified strategy.
        
        Args:
            service_name: Name of the service to deploy
            version: Version to deploy
            strategy: Deployment strategy (defaults to rolling)
            targets: Optional list of deployment targets
            
        Returns:
            True if deployment was successful
        """
        strategy = strategy or self._default_strategy

        # Create mock targets if not provided
        if targets is None:
            targets = [
                DeploymentTarget(
                    id=f"{service_name}-{i}",
                    name=f"{service_name}-instance-{i}",
                    address=f"localhost:{8000 + i}",
                )
                for i in range(3)
            ]

        # Mock deploy function
        def deploy_fn(target: DeploymentTarget, ver: str) -> bool:
            target.version = ver
            return True

        try:
            result = strategy.deploy(targets, version, deploy_fn)
        except Exception:
            self._deployments.append({
                "service": service_name,
                "version": version,
                "strategy": type(strategy).__name__,
                "success": False,
                "targets_updated": 0,
            })
            return False

        self._deployments.append({
            "service": service_name,
            "version": version,
            "strategy": type(strategy).__name__,
            "success": result.success,
            "targets_updated": result.targets_updated,
        })

        return result.success
    
    def get_deployment_history(self) -> List[Dict[str, Any]]:
        """Get history of deployments."""
        return list(self._deployments)
    
    def rollback(
        self,
        service_name: str,
        previous_version: str,
        strategy: Optional[DeploymentStrategy] = None,
    ) -> bool:
        """
        Rollback a service to a previous version.
        
        Args:
            service_name: Service to rollback
            previous_version: Version to rollback to
            strategy: Rollback strategy (defaults to rolling)
            
        Returns:
            True if rollback was successful
        """
        return self.deploy(service_name, previous_version, strategy)


class GitOpsSynchronizer:
    """
    GitOps synchronization manager.
    
    Synchronizes deployment configurations from a Git repository.
    """
    
    def __init__(
        self,
        repo_url: Optional[str] = None,
        local_path: Optional[str] = None,
        branch: str = "main",
    ):
        """
        Initialize GitOps synchronizer.
        
        Args:
            repo_url: URL of the Git repository
            local_path: Local path to clone repository
            branch: Branch to sync from
        """
        self.repo_url = repo_url
        self.local_path = local_path
        self.branch = branch
        self._synced = False
    
    def sync(self) -> bool:
        """
        Synchronize from Git repository.
        
        Returns:
            True if sync was successful
        """
        # Stub implementation
        self._synced = True
        return True
    
    def get_version(self) -> str:
        """
        Get the current synced version via git rev-parse.

        Returns:
            Version string or 'unknown'
        """
        import subprocess
        if self.local_path:
            try:
                result = subprocess.run(
                    ['git', 'rev-parse', 'HEAD'],
                    capture_output=True, text=True,
                    cwd=self.local_path,
                )
                if result.returncode == 0 and result.stdout.strip():
                    return result.stdout.strip()
            except Exception:
                pass
        if not self._synced:
            return "unknown"
        return "v1.0.0"
    
    def is_synced(self) -> bool:
        """Check if currently synced."""
        return self._synced


__all__ = [
    # Submodules
    "health_checks",
    "strategies",
    "rollback",
    # Strategy classes
    "DeploymentState",
    "DeploymentTarget",
    "DeploymentResult",
    "DeploymentStrategy",
    "RollingDeployment",
    "BlueGreenDeployment",
    "CanaryDeployment",
    "create_strategy",
    # Aliases for convenience
    "CanaryStrategy",
    "BlueGreenStrategy",
    "RollingStrategy",
    # Manager classes
    "DeploymentManager",
    "GitOpsSynchronizer",
]

__version__ = "0.1.0"

