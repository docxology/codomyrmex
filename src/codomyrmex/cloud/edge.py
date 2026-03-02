"""
Edge Computing Provider Support

Support for edge computing providers: Cloudflare Workers, Fastly Compute@Edge, etc.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class EdgeProvider(Enum):
    """Supported edge providers."""
    CLOUDFLARE_WORKERS = "cloudflare_workers"
    FASTLY_COMPUTE = "fastly_compute"
    AWS_LAMBDA_EDGE = "aws_lambda_edge"
    VERCEL_EDGE = "vercel_edge"
    DENO_DEPLOY = "deno_deploy"


class EdgeRegion(Enum):
    """Common edge regions."""
    GLOBAL = "global"
    US_EAST = "us-east"
    US_WEST = "us-west"
    EUROPE = "europe"
    ASIA_PACIFIC = "asia-pacific"


@dataclass
class EdgeFunctionConfig:
    """Configuration for an edge function."""
    name: str
    provider: EdgeProvider
    entry_point: str = "handler"
    runtime: str = "javascript"
    memory_mb: int = 128
    timeout_seconds: int = 30
    environment: dict[str, str] = field(default_factory=dict)
    routes: list[str] = field(default_factory=list)
    regions: list[EdgeRegion] = field(default_factory=lambda: [EdgeRegion.GLOBAL])
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class EdgeDeployment:
    """An edge function deployment."""
    id: str
    function_name: str
    provider: EdgeProvider
    version: str
    url: str = ""
    deployed_at: datetime = field(default_factory=datetime.now)
    regions: list[EdgeRegion] = field(default_factory=list)
    status: str = "active"


class EdgeClient(ABC):
    """Abstract base class for edge provider clients."""

    @property
    @abstractmethod
    def provider(self) -> EdgeProvider:
        """provider ."""
        pass

    @abstractmethod
    def deploy(self, config: EdgeFunctionConfig, code: str) -> EdgeDeployment:
        """Deploy edge function."""
        pass

    @abstractmethod
    def list_deployments(self) -> list[EdgeDeployment]:
        """List all deployments."""
        pass

    @abstractmethod
    def delete(self, deployment_id: str) -> bool:
        """Delete a deployment."""
        pass

    @abstractmethod
    def get_logs(self, deployment_id: str, limit: int = 100) -> list[dict[str, Any]]:
        """Get deployment logs."""
        pass


class CloudflareWorkersClient(EdgeClient):
    """Cloudflare Workers client (in-memory implementation)."""

    def __init__(self, account_id: str, api_token: str):
        self.account_id = account_id
        self.api_token = api_token
        self._deployments: dict[str, EdgeDeployment] = {}
        self._counter = 0

    @property
    def provider(self) -> EdgeProvider:
        """provider ."""
        return EdgeProvider.CLOUDFLARE_WORKERS

    def deploy(self, config: EdgeFunctionConfig, code: str) -> EdgeDeployment:
        """Deploy to Cloudflare Workers."""
        self._counter += 1
        deployment = EdgeDeployment(
            id=f"cf-{self._counter}",
            function_name=config.name,
            provider=self.provider,
            version=f"v{self._counter}",
            url=f"https://{config.name}.{self.account_id}.workers.dev",
            regions=config.regions,
        )
        self._deployments[deployment.id] = deployment
        return deployment

    def list_deployments(self) -> list[EdgeDeployment]:
        return list(self._deployments.values())

    def delete(self, deployment_id: str) -> bool:
        """Delete the specified resource."""
        if deployment_id in self._deployments:
            del self._deployments[deployment_id]
            return True
        return False

    def get_logs(self, deployment_id: str, limit: int = 100) -> list[dict[str, Any]]:
        return []


class FastlyComputeClient(EdgeClient):
    """Fastly Compute@Edge client (in-memory implementation)."""

    def __init__(self, api_key: str, service_id: str = ""):
        self.api_key = api_key
        self.service_id = service_id
        self._deployments: dict[str, EdgeDeployment] = {}
        self._counter = 0

    @property
    def provider(self) -> EdgeProvider:
        """provider ."""
        return EdgeProvider.FASTLY_COMPUTE

    def deploy(self, config: EdgeFunctionConfig, code: str) -> EdgeDeployment:
        """Deploy to Fastly Compute@Edge."""
        self._counter += 1
        deployment = EdgeDeployment(
            id=f"fastly-{self._counter}",
            function_name=config.name,
            provider=self.provider,
            version=f"v{self._counter}",
            url=f"https://{self.service_id}.edgecompute.app",
            regions=config.regions,
        )
        self._deployments[deployment.id] = deployment
        return deployment

    def list_deployments(self) -> list[EdgeDeployment]:
        return list(self._deployments.values())

    def delete(self, deployment_id: str) -> bool:
        """Delete the specified resource."""
        if deployment_id in self._deployments:
            del self._deployments[deployment_id]
            return True
        return False

    def get_logs(self, deployment_id: str, limit: int = 100) -> list[dict[str, Any]]:
        return []


class EdgeManager:
    """Manage edge deployments across providers."""

    def __init__(self):
        self._clients: dict[EdgeProvider, EdgeClient] = {}

    def register_client(self, client: EdgeClient) -> None:
        """Register an edge provider client."""
        self._clients[client.provider] = client

    def get_client(self, provider: EdgeProvider) -> EdgeClient | None:
        """Get a registered client."""
        return self._clients.get(provider)

    def deploy(
        self,
        config: EdgeFunctionConfig,
        code: str,
    ) -> EdgeDeployment:
        """Deploy to specified provider."""
        client = self._clients.get(config.provider)
        if not client:
            raise ValueError(f"No client registered for {config.provider}")
        return client.deploy(config, code)

    def list_all_deployments(self) -> dict[EdgeProvider, list[EdgeDeployment]]:
        """List deployments from all providers."""
        return {
            provider: client.list_deployments()
            for provider, client in self._clients.items()
        }


__all__ = [
    "EdgeProvider",
    "EdgeRegion",
    "EdgeFunctionConfig",
    "EdgeDeployment",
    "EdgeClient",
    "CloudflareWorkersClient",
    "FastlyComputeClient",
    "EdgeManager",
]
