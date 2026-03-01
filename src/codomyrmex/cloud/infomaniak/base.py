"""
Infomaniak Base Client Classes.

Provides shared functionality for all Infomaniak cloud clients,
eliminating factory method duplication across 8+ client modules.

Three base classes cover all auth mechanisms:
- InfomaniakOpenStackBase: OpenStack SDK with Application Credentials
- InfomaniakS3Base: boto3 S3 with access key / secret key
- InfomaniakRESTBase: REST API with OAuth2 Bearer token
"""

import logging
from typing import Any

import requests

logger = logging.getLogger(__name__)


class InfomaniakOpenStackBase:
    """
    Base class for Infomaniak clients using OpenStack SDK.

    Provides shared __init__, from_env(), from_credentials(),
    context manager protocol, and connection validation.

    Subclasses should set ``_service_name`` for error reporting.
    """

    _service_name: str = "openstack"

    def __init__(self, connection: Any):
        """
        Initialize with an OpenStack connection.

        Args:
            connection: openstack.connection.Connection object
        """
        self._conn = connection

    @classmethod
    def from_env(cls) -> "InfomaniakOpenStackBase":
        """Create client using environment variable credentials."""
        from .auth import create_openstack_connection

        conn = create_openstack_connection()
        return cls(conn)

    @classmethod
    def from_credentials(
        cls,
        application_credential_id: str,
        application_credential_secret: str,
        auth_url: str | None = None,
        region: str = "dc3-a",
    ) -> "InfomaniakOpenStackBase":
        """
        Create client with explicit credentials.

        Args:
            application_credential_id: Infomaniak app credential ID
            application_credential_secret: Infomaniak app credential secret
            auth_url: Optional auth URL override
            region: Region name
        """
        from .auth import InfomaniakCredentials, create_openstack_connection

        creds = InfomaniakCredentials(
            application_credential_id=application_credential_id,
            application_credential_secret=application_credential_secret,
            auth_url=auth_url or "https://api.pub1.infomaniak.cloud/identity/v3/",
            region=region,
        )
        conn = create_openstack_connection(creds)
        return cls(conn)

    def __enter__(self):
        """Execute   Enter   operations natively."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Execute   Exit   operations natively."""
        self.close()
        return False

    def close(self):
        """Safely close the OpenStack connection."""
        if hasattr(self._conn, "close"):
            try:
                self._conn.close()
            except Exception as e:
                logger.warning(f"Error closing {self._service_name} connection: {e}")

    def validate_connection(self) -> bool:
        """
        Lightweight health check by listing projects.

        Returns:
            True if the connection is valid
        """
        try:
            list(self._conn.identity.projects())
            return True
        except Exception as e:
            logger.error(f"Connection validation failed for {self._service_name}: {e}")
            return False


class InfomaniakS3Base:
    """
    Base class for Infomaniak S3-compatible clients using boto3.

    Provides shared __init__, from_env(), from_credentials(),
    context manager protocol, and connection validation.
    """

    DEFAULT_ENDPOINT = "https://s3.pub1.infomaniak.cloud/"
    DEFAULT_REGION = "us-east-1"

    def __init__(self, client: Any):
        """
        Initialize with a boto3 S3 client.

        Args:
            client: boto3.client('s3') instance
        """
        self._client = client

    @classmethod
    def from_env(cls) -> "InfomaniakS3Base":
        """Create client using environment variable credentials."""
        from .auth import create_s3_client

        client = create_s3_client()
        return cls(client)

    @classmethod
    def from_credentials(
        cls,
        access_key: str,
        secret_key: str,
        endpoint_url: str | None = None,
        region: str | None = None,
    ) -> "InfomaniakS3Base":
        """Create client with explicit credentials."""
        try:
            import boto3
        except ImportError:
            raise ImportError("boto3 is required for S3 operations")

        client = boto3.client(
            "s3",
            endpoint_url=endpoint_url or cls.DEFAULT_ENDPOINT,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region or cls.DEFAULT_REGION,
        )
        return cls(client)

    def __enter__(self):
        """Execute   Enter   operations natively."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Execute   Exit   operations natively."""
        self.close()
        return False

    def close(self):
        """Close the S3 client (no-op for boto3, but provided for consistency)."""
        return None  # boto3 session cleanup handled by GC

    def validate_connection(self) -> bool:
        """
        Lightweight health check by listing buckets.

        Returns:
            True if the connection is valid
        """
        try:
            self._client.list_buckets()
            return True
        except Exception as e:
            logger.error(f"S3 connection validation failed: {e}")
            return False


class InfomaniakRESTBase:
    """
    Base class for Infomaniak REST API clients using Bearer token auth.

    Provides shared __init__, from_env(), context manager protocol,
    and connection validation for REST-based Infomaniak services
    (e.g., Newsletter API).

    Subclasses should set ``_service_name`` for error reporting and
    override ``from_env()`` with service-specific env var names.
    """

    _service_name: str = "rest"

    def __init__(self, token: str, base_url: str = "https://api.infomaniak.com"):
        """
        Initialize with a Bearer token.

        Args:
            token: OAuth2 bearer token for API authentication.
            base_url: API base URL (default: https://api.infomaniak.com).
        """
        self._token = token
        self._base_url = base_url.rstrip("/")
        self._session = requests.Session()
        self._session.headers.update({
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        })

    @classmethod
    def from_env(cls, **kwargs) -> "InfomaniakRESTBase":
        """Create client from environment variables.

        Subclasses should override to define service-specific env var names.
        """
        raise NotImplementedError(
            f"{cls.__name__} must override from_env() with service-specific env vars"
        )

    def __enter__(self):
        """Execute   Enter   operations natively."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Execute   Exit   operations natively."""
        self.close()
        return False

    def close(self):
        """Close the requests session."""
        if hasattr(self, "_session") and hasattr(self._session, "close"):
            try:
                self._session.close()
            except Exception as e:
                logger.warning(f"Error closing {self._service_name} session: {e}")

    def validate_connection(self) -> bool:
        """
        Lightweight health check — subclasses should override with
        a service-specific GET request.

        Returns:
            True if the connection is valid.
        """
        return True
