"""
Cloud common utilities.

Provides common abstractions for cloud operations.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class CloudProvider(Enum):
    """Supported cloud providers."""
    AWS = "aws"
    GCP = "gcp"
    AZURE = "azure"
    INFOMANIAK = "infomaniak"
    LOCAL = "local"


class ResourceType(Enum):
    """Types of cloud resources."""
    COMPUTE = "compute"
    STORAGE = "storage"
    DATABASE = "database"
    NETWORK = "network"
    SERVERLESS = "serverless"
    CONTAINER = "container"
    QUEUE = "queue"


@dataclass
class CloudCredentials:
    """Credentials for cloud access."""
    provider: CloudProvider
    access_key: str | None = None
    secret_key: str | None = None
    region: str = "us-east-1"
    project_id: str | None = None
    profile: str | None = None
    metadata: dict[str, str] = field(default_factory=dict)


@dataclass
class CloudResource:
    """A cloud resource."""
    id: str
    name: str
    resource_type: ResourceType
    provider: CloudProvider
    region: str
    status: str = "active"
    created_at: datetime | None = None
    tags: dict[str, str] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Execute To Dict operations natively."""
        return {
            "id": self.id,
            "name": self.name,
            "type": self.resource_type.value,
            "provider": self.provider.value,
            "region": self.region,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "tags": self.tags,
        }


class CloudClient(ABC):
    """Abstract base class for cloud clients."""

    provider: CloudProvider

    def __init__(self, credentials: CloudCredentials):
        """Execute   Init   operations natively."""
        self.credentials = credentials
        self.region = credentials.region

    @abstractmethod
    def list_resources(
        self,
        resource_type: ResourceType | None = None,
    ) -> list[CloudResource]:
        """List cloud resources."""
        pass

    @abstractmethod
    def get_resource(self, resource_id: str) -> CloudResource | None:
        """Get a specific resource."""
        pass

    @abstractmethod
    def create_resource(
        self,
        name: str,
        resource_type: ResourceType,
        config: dict[str, Any],
    ) -> CloudResource:
        """Create a new resource."""
        pass

    @abstractmethod
    def delete_resource(self, resource_id: str) -> bool:
        """Delete a resource."""
        pass


class StorageClient(ABC):
    """Abstract storage client."""

    @abstractmethod
    def list_buckets(self) -> list[str]:
        """List storage buckets."""
        pass

    @abstractmethod
    def create_bucket(self, name: str) -> bool:
        """Create a bucket."""
        pass

    @abstractmethod
    def upload_file(
        self,
        bucket: str,
        key: str,
        data: bytes,
        content_type: str | None = None,
    ) -> str:
        """Upload a file."""
        pass

    @abstractmethod
    def download_file(self, bucket: str, key: str) -> bytes:
        """Download a file."""
        pass

    @abstractmethod
    def delete_file(self, bucket: str, key: str) -> bool:
        """Delete a file."""
        pass

    @abstractmethod
    def generate_presigned_url(
        self,
        bucket: str,
        key: str,
        expires_in: int = 3600,
    ) -> str:
        """Generate a presigned URL."""
        pass


class ComputeClient(ABC):
    """Abstract compute client."""

    @abstractmethod
    def list_instances(self) -> list[dict[str, Any]]:
        """List compute instances."""
        pass

    @abstractmethod
    def start_instance(self, instance_id: str) -> bool:
        """Start an instance."""
        pass

    @abstractmethod
    def stop_instance(self, instance_id: str) -> bool:
        """Stop an instance."""
        pass

    @abstractmethod
    def terminate_instance(self, instance_id: str) -> bool:
        """Terminate an instance."""
        pass

    @abstractmethod
    def create_instance(
        self,
        name: str,
        instance_type: str,
        image_id: str,
        **kwargs
    ) -> dict[str, Any]:
        """Create a new instance."""
        pass


class ServerlessClient(ABC):
    """Abstract serverless client."""

    @abstractmethod
    def list_functions(self) -> list[dict[str, Any]]:
        """List serverless functions."""
        pass

    @abstractmethod
    def invoke_function(
        self,
        function_name: str,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        """Invoke a function."""
        pass

    @abstractmethod
    def create_function(
        self,
        name: str,
        runtime: str,
        handler: str,
        code_path: str,
        **kwargs
    ) -> dict[str, Any]:
        """Create a new function."""
        pass

    @abstractmethod
    def delete_function(self, function_name: str) -> bool:
        """Delete a function."""
        pass


class CloudConfig:
    """Configuration for cloud operations."""

    def __init__(self):
        """Execute   Init   operations natively."""
        self._providers: dict[CloudProvider, CloudCredentials] = {}

    def add_provider(self, credentials: CloudCredentials) -> None:
        """Add provider credentials."""
        self._providers[credentials.provider] = credentials

    def get_credentials(self, provider: CloudProvider) -> CloudCredentials | None:
        """Get credentials for a provider."""
        return self._providers.get(provider)

    def has_provider(self, provider: CloudProvider) -> bool:
        """Check if provider is configured."""
        return provider in self._providers

    @classmethod
    def from_env(cls) -> 'CloudConfig':
        """Create config from environment variables."""
        import os

        config = cls()

        # AWS
        if os.environ.get('AWS_ACCESS_KEY_ID'):
            config.add_provider(CloudCredentials(
                provider=CloudProvider.AWS,
                access_key=os.environ.get('AWS_ACCESS_KEY_ID'),
                secret_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
                region=os.environ.get('AWS_DEFAULT_REGION', 'us-east-1'),
            ))

        # GCP
        if os.environ.get('GOOGLE_APPLICATION_CREDENTIALS'):
            config.add_provider(CloudCredentials(
                provider=CloudProvider.GCP,
                project_id=os.environ.get('GCP_PROJECT_ID'),
                region=os.environ.get('GCP_REGION', 'us-central1'),
            ))

        # Infomaniak
        if os.environ.get('INFOMANIAK_APP_CREDENTIAL_ID'):
            config.add_provider(CloudCredentials(
                provider=CloudProvider.INFOMANIAK,
                access_key=os.environ.get('INFOMANIAK_APP_CREDENTIAL_ID'),
                secret_key=os.environ.get('INFOMANIAK_APP_CREDENTIAL_SECRET'),
                region=os.environ.get('INFOMANIAK_REGION', 'dc3-a'),
                project_id=os.environ.get('INFOMANIAK_PROJECT_ID'),
            ))

        return config


__all__ = [
    "CloudProvider",
    "ResourceType",
    "CloudCredentials",
    "CloudResource",
    "CloudClient",
    "StorageClient",
    "ComputeClient",
    "ServerlessClient",
    "CloudConfig",
]
