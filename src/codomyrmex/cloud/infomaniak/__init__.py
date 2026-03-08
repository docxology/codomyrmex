"""
Infomaniak Public Cloud Integration.

This module provides comprehensive APIs for interacting with Infomaniak's
OpenStack-based cloud platform, including:

- Compute: Instance management via Nova
- Block Storage: Volume management via Cinder
- Network: Networking via Neutron and Load Balancers via Octavia
- Object Storage: Swift API and S3-compatible storage
- Identity: Application credentials and EC2 credentials via Keystone
- DNS: DNS zones and reverse DNS via Designate
- Orchestration: Heat stack management
- Metering: Billing and usage metrics

Usage:
    from codomyrmex.cloud.infomaniak import InfomaniakComputeClient

    # From environment variables
    client = InfomaniakComputeClient.from_env()
    instances = client.list_instances()

    # From explicit credentials
    client = InfomaniakComputeClient.from_credentials(
        application_credential_id="your-id",
        application_credential_secret="your-secret",
    )

Environment Variables:
    INFOMANIAK_AUTH_URL: Identity endpoint (default: pub1.infomaniak.cloud)
    INFOMANIAK_APP_CREDENTIAL_ID: Application credential ID
    INFOMANIAK_APP_CREDENTIAL_SECRET: Application credential secret
    INFOMANIAK_PROJECT_ID: Project ID for scoped operations
    INFOMANIAK_S3_ACCESS_KEY: S3 access key for object storage
    INFOMANIAK_S3_SECRET_KEY: S3 secret key for object storage
"""

# Exception hierarchy
# Core authentication
import contextlib

from .auth import (
    InfomaniakCredentials,
    InfomaniakS3Credentials,
    create_openstack_connection,
    create_s3_client,
)

# Base classes
from .base import InfomaniakOpenStackBase, InfomaniakRESTBase, InfomaniakS3Base
from .exceptions import (
    InfomaniakAuthError,
    InfomaniakCloudError,
    InfomaniakConflictError,
    InfomaniakConnectionError,
    InfomaniakNotFoundError,
    InfomaniakQuotaExceededError,
    InfomaniakTimeoutError,
    classify_http_error,
    classify_openstack_error,
)

# Direct imports for type checking and direct access
with contextlib.suppress(ImportError):
    from .compute import InfomaniakComputeClient

with contextlib.suppress(ImportError):
    from .block_storage import InfomaniakVolumeClient

with contextlib.suppress(ImportError):
    from .network import InfomaniakNetworkClient

with contextlib.suppress(ImportError):
    from .object_storage import InfomaniakObjectStorageClient, InfomaniakS3Client

with contextlib.suppress(ImportError):
    from .identity import InfomaniakIdentityClient

with contextlib.suppress(ImportError):
    from .dns import InfomaniakDNSClient

with contextlib.suppress(ImportError):
    from .orchestration import InfomaniakHeatClient

with contextlib.suppress(ImportError):
    from .metering import InfomaniakMeteringClient

with contextlib.suppress(ImportError):
    from .newsletter import InfomaniakNewsletterClient


__all__ = [
    "InfomaniakAuthError",
    # Exceptions
    "InfomaniakCloudError",
    # Clients
    "InfomaniakComputeClient",
    "InfomaniakConflictError",
    "InfomaniakConnectionError",
    # Authentication
    "InfomaniakCredentials",
    "InfomaniakDNSClient",
    "InfomaniakHeatClient",
    "InfomaniakIdentityClient",
    "InfomaniakMeteringClient",
    "InfomaniakNetworkClient",
    "InfomaniakNewsletterClient",
    "InfomaniakNotFoundError",
    "InfomaniakObjectStorageClient",
    # Base classes
    "InfomaniakOpenStackBase",
    "InfomaniakQuotaExceededError",
    "InfomaniakRESTBase",
    "InfomaniakS3Base",
    "InfomaniakS3Client",
    "InfomaniakS3Credentials",
    "InfomaniakTimeoutError",
    "InfomaniakVolumeClient",
    "classify_http_error",
    "classify_openstack_error",
    "create_openstack_connection",
    "create_s3_client",
]
