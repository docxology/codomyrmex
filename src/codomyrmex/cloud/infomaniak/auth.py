"""
Infomaniak Authentication Utilities.

Provides credential management and OpenStack connection creation
for Infomaniak Public Cloud services.

Endpoints:
    - Identity (Keystone): https://api.pub1.infomaniak.cloud/identity/v3/
    - S3 Object Storage: https://s3.pub1.infomaniak.cloud/
    - S3 Object Storage (alt): https://s3.pub2.infomaniak.cloud/
"""

import os
from dataclasses import dataclass, field
from typing import Any

logger = get_logger(__name__)

from .exceptions import InfomaniakAuthError
from codomyrmex.logging_monitoring.core.logger_config import get_logger

# Default Infomaniak endpoints
DEFAULT_AUTH_URL = "https://api.pub1.infomaniak.cloud/identity/v3/"
DEFAULT_S3_ENDPOINT = "https://s3.pub1.infomaniak.cloud/"
DEFAULT_S3_REGION = "us-east-1"  # S3-compatible default region




@dataclass
class InfomaniakCredentials:
    """
    Credentials for Infomaniak OpenStack services.

    Uses Application Credentials for secure programmatic access.
    These are project-scoped tokens created in the Infomaniak dashboard.

    Attributes:
        application_credential_id: The credential ID from Infomaniak
        application_credential_secret: The credential secret
        auth_url: Keystone identity endpoint
        project_id: Optional project ID for scoped operations
        region: Region name (default: dc3-a)
    """
    application_credential_id: str
    application_credential_secret: str
    auth_url: str = DEFAULT_AUTH_URL
    project_id: str | None = None
    region: str = "dc3-a"
    metadata: dict[str, str] = field(default_factory=dict)

    @classmethod
    def from_env(cls) -> "InfomaniakCredentials":
        """
        Create credentials from environment variables.

        Environment Variables:
            INFOMANIAK_APP_CREDENTIAL_ID: Application credential ID
            INFOMANIAK_APP_CREDENTIAL_SECRET: Application credential secret
            INFOMANIAK_AUTH_URL: Optional auth URL override
            INFOMANIAK_PROJECT_ID: Optional project ID
            INFOMANIAK_REGION: Optional region override

        Returns:
            InfomaniakCredentials instance

        Raises:
            InfomaniakAuthError: If required credentials are missing
        """
        credential_id = os.environ.get("INFOMANIAK_APP_CREDENTIAL_ID")
        credential_secret = os.environ.get("INFOMANIAK_APP_CREDENTIAL_SECRET")

        if not credential_id or not credential_secret:
            raise InfomaniakAuthError(
                "Missing required environment variables: "
                "INFOMANIAK_APP_CREDENTIAL_ID and INFOMANIAK_APP_CREDENTIAL_SECRET"
            )

        return cls(
            application_credential_id=credential_id,
            application_credential_secret=credential_secret,
            auth_url=os.environ.get("INFOMANIAK_AUTH_URL", DEFAULT_AUTH_URL),
            project_id=os.environ.get("INFOMANIAK_PROJECT_ID"),
            region=os.environ.get("INFOMANIAK_REGION", "dc3-a"),
        )

    def to_openstack_auth(self) -> dict[str, Any]:
        """Convert to OpenStack SDK auth dict format."""
        return {
            "auth_url": self.auth_url,
            "application_credential_id": self.application_credential_id,
            "application_credential_secret": self.application_credential_secret,
        }


@dataclass
class InfomaniakS3Credentials:
    """
    Credentials for Infomaniak S3-compatible Object Storage.

    These are EC2-style credentials created via the OpenStack CLI:
        openstack ec2 credentials create

    Attributes:
        access_key: S3 access key ID
        secret_key: S3 secret access key
        endpoint_url: S3 endpoint URL
        region: S3 region (default: us-east-1 for compatibility)
    """
    access_key: str
    secret_key: str
    endpoint_url: str = DEFAULT_S3_ENDPOINT
    region: str = DEFAULT_S3_REGION

    @classmethod
    def from_env(cls) -> "InfomaniakS3Credentials":
        """
        Create S3 credentials from environment variables.

        Environment Variables:
            INFOMANIAK_S3_ACCESS_KEY: S3 access key
            INFOMANIAK_S3_SECRET_KEY: S3 secret key
            INFOMANIAK_S3_ENDPOINT: Optional endpoint override
            INFOMANIAK_S3_REGION: Optional region override

        Returns:
            InfomaniakS3Credentials instance

        Raises:
            InfomaniakAuthError: If required credentials are missing
        """
        access_key = os.environ.get("INFOMANIAK_S3_ACCESS_KEY")
        secret_key = os.environ.get("INFOMANIAK_S3_SECRET_KEY")

        if not access_key or not secret_key:
            raise InfomaniakAuthError(
                "Missing required environment variables: "
                "INFOMANIAK_S3_ACCESS_KEY and INFOMANIAK_S3_SECRET_KEY"
            )

        return cls(
            access_key=access_key,
            secret_key=secret_key,
            endpoint_url=os.environ.get("INFOMANIAK_S3_ENDPOINT", DEFAULT_S3_ENDPOINT),
            region=os.environ.get("INFOMANIAK_S3_REGION", DEFAULT_S3_REGION),
        )


def create_openstack_connection(
    credentials: InfomaniakCredentials | None = None,
    **kwargs
) -> Any:
    """
    Create an OpenStack SDK connection to Infomaniak.

    Args:
        credentials: InfomaniakCredentials instance. If None, reads from env.
        **kwargs: Additional arguments passed to openstack.connect()

    Returns:
        openstack.connection.Connection object

    Raises:
        ImportError: If openstacksdk is not installed
        InfomaniakAuthError: If authentication fails
    """
    try:
        import openstack
    except ImportError:
        raise ImportError(
            "openstacksdk is required for Infomaniak integration. "
            "Install with: pip install openstacksdk"
        ) from None

    if credentials is None:
        credentials = InfomaniakCredentials.from_env()

    try:
        conn = openstack.connect(
            auth_type="v3applicationcredential",
            auth_url=credentials.auth_url,
            application_credential_id=credentials.application_credential_id,
            application_credential_secret=credentials.application_credential_secret,
            region_name=credentials.region,
            **kwargs
        )
        logger.info(f"Connected to Infomaniak cloud at {credentials.auth_url}")
        return conn
    except Exception as e:
        logger.error(f"Failed to connect to Infomaniak: {e}")
        raise InfomaniakAuthError(f"Authentication failed: {e}") from e


def create_s3_client(
    credentials: InfomaniakS3Credentials | None = None,
    **kwargs
) -> Any:
    """
    Create a boto3 S3 client for Infomaniak Object Storage.

    Args:
        credentials: InfomaniakS3Credentials instance. If None, reads from env.
        **kwargs: Additional arguments passed to boto3.client()

    Returns:
        boto3.client('s3') configured for Infomaniak

    Raises:
        ImportError: If boto3 is not installed
        InfomaniakAuthError: If credentials are missing
    """
    try:
        import boto3
    except ImportError:
        raise ImportError(
            "boto3 is required for Infomaniak S3 integration. "
            "Install with: pip install boto3"
        ) from None

    if credentials is None:
        credentials = InfomaniakS3Credentials.from_env()

    client = boto3.client(
        "s3",
        endpoint_url=credentials.endpoint_url,
        aws_access_key_id=credentials.access_key,
        aws_secret_access_key=credentials.secret_key,
        region_name=credentials.region,
        **kwargs
    )
    logger.info(f"Created S3 client for {credentials.endpoint_url}")
    return client
