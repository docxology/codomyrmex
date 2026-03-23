"""
Cloud common utilities.

Provides common abstractions for cloud operations.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional


class CloudProvider(Enum):
    """Supported cloud providers."""

    AWS = "aws"
    GCP = "gcp"
    AZURE = "azure"
    INFOMANIAK = "infomaniak"
    CODA = "coda"
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
    DOCUMENT = "document"


class CloudError(Exception):
    """Base class for cloud-related errors."""

    def __init__(self, message: str, provider: CloudProvider | None = None, **kwargs):
        super().__init__(message)
        self.provider = provider
        self.metadata = kwargs


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
        return {
            "id": self.id,
            "name": self.name,
            "type": self.resource_type.value,
            "provider": self.provider.value,
            "region": self.region,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "tags": self.tags,
            "metadata": self.metadata,
        }


class CloudClient(ABC):
    """Abstract base class for cloud clients."""

    provider: CloudProvider

    def __init__(self, credentials: CloudCredentials | None = None):
        self.credentials = credentials
        self.region = credentials.region if credentials else None

    @abstractmethod
    def list_resources(
        self,
        resource_type: ResourceType | None = None,
    ) -> list[CloudResource]:
        """list cloud resources."""

    @abstractmethod
    def get_resource(self, resource_id: str) -> CloudResource | None:
        """Get a specific resource."""

    @abstractmethod
    def create_resource(
        self,
        name: str,
        resource_type: ResourceType,
        config: dict[str, Any],
    ) -> CloudResource:
        """Create a new resource."""

    @abstractmethod
    def delete_resource(self, resource_id: str) -> bool:
        """Delete a resource."""


class StorageClient(ABC):
    """Abstract storage client."""

    @abstractmethod
    def list_buckets(self) -> list[str]:
        """list storage buckets."""

    @abstractmethod
    def create_bucket(self, name: str, region: str | None = None) -> bool:
        """Create a bucket."""

    @abstractmethod
    def delete_bucket(self, name: str) -> bool:
        """Delete a bucket."""

    @abstractmethod
    def bucket_exists(self, name: str) -> bool:
        """Check if a bucket exists."""

    @abstractmethod
    def upload_file(
        self,
        bucket: str,
        key: str,
        file_path: str,
        content_type: str | None = None,
    ) -> bool:
        """Upload a file from local disk."""

    @abstractmethod
    def download_file(self, bucket: str, key: str, file_path: str) -> bool:
        """Download a file to local disk."""

    @abstractmethod
    def list_objects(self, bucket: str, prefix: str | None = None) -> list[str]:
        """list objects in a bucket."""

    @abstractmethod
    def delete_object(self, bucket: str, key: str) -> bool:
        """Delete an object."""

    @abstractmethod
    def get_object_metadata(self, bucket: str, key: str) -> dict[str, Any]:
        """Get object metadata."""

    @abstractmethod
    def generate_presigned_url(
        self,
        bucket: str,
        key: str,
        expires_in: int = 3600,
        operation: str = "get_object",
    ) -> str:
        """Generate a presigned URL."""


class ComputeClient(ABC):
    """Abstract compute client."""

    @abstractmethod
    def list_instances(self) -> list[dict[str, Any]]:
        """list compute instances."""

    @abstractmethod
    def start_instance(self, instance_id: str) -> bool:
        """Start an instance."""

    @abstractmethod
    def stop_instance(self, instance_id: str) -> bool:
        """Stop an instance."""

    @abstractmethod
    def terminate_instance(self, instance_id: str) -> bool:
        """Terminate an instance."""

    @abstractmethod
    def create_instance(
        self, name: str, instance_type: str, image_id: str, **kwargs
    ) -> dict[str, Any]:
        """Create a new instance."""


class ServerlessClient(ABC):
    """Abstract serverless client."""

    @abstractmethod
    def list_functions(self) -> list[dict[str, Any]]:
        """list serverless functions."""

    @abstractmethod
    def invoke_function(
        self,
        function_name: str,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        """Invoke a function."""

    @abstractmethod
    def create_function(
        self, name: str, runtime: str, handler: str, code_path: str, **kwargs
    ) -> dict[str, Any]:
        """Create a new function."""

    @abstractmethod
    def delete_function(self, function_name: str) -> bool:
        """Delete a function."""


class CloudConfig:
    """Configuration for cloud operations."""

    def __init__(self):
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
    def from_env(cls) -> "CloudConfig":
        """Create config from environment variables."""
        import os

        config = cls()

        # AWS
        if os.environ.get("AWS_ACCESS_KEY_ID"):
            config.add_provider(
                CloudCredentials(
                    provider=CloudProvider.AWS,
                    access_key=os.environ.get("AWS_ACCESS_KEY_ID"),
                    secret_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
                    region=os.environ.get("AWS_DEFAULT_REGION", "us-east-1"),
                )
            )

        # GCP
        if os.environ.get("GOOGLE_APPLICATION_CREDENTIALS") or os.environ.get(
            "GCP_PROJECT_ID"
        ):
            config.add_provider(
                CloudCredentials(
                    provider=CloudProvider.GCP,
                    project_id=os.environ.get("GCP_PROJECT_ID"),
                    region=os.environ.get("GCP_REGION", "us-central1"),
                )
            )

        # Infomaniak
        if os.environ.get("INFOMANIAK_APP_CREDENTIAL_ID"):
            config.add_provider(
                CloudCredentials(
                    provider=CloudProvider.INFOMANIAK,
                    access_key=os.environ.get("INFOMANIAK_APP_CREDENTIAL_ID"),
                    secret_key=os.environ.get("INFOMANIAK_APP_CREDENTIAL_SECRET"),
                    region=os.environ.get("INFOMANIAK_REGION", "dc3-a"),
                    project_id=os.environ.get("INFOMANIAK_PROJECT_ID"),
                )
            )

        # Coda
        if os.environ.get("CODA_API_TOKEN"):
            config.add_provider(
                CloudCredentials(
                    provider=CloudProvider.CODA,
                    access_key=os.environ.get("CODA_API_TOKEN"),
                )
            )

        return config


from .rate_limiter import (
    RateLimiterConfig,
    TokenBucketLimiter,
    get_provider_limiter,
    rate_limited,
    reset_all_limiters,
)

__all__ = [
    "CloudClient",
    "CloudConfig",
    "CloudCredentials",
    "CloudError",
    "CloudProvider",
    "CloudResource",
    "ComputeClient",
    "RateLimiterConfig",
    "ResourceType",
    "ServerlessClient",
    "StorageClient",
    "TokenBucketLimiter",
    "get_provider_limiter",
    "rate_limited",
    "reset_all_limiters",
]
