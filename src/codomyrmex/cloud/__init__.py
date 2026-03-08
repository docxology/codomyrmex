"""
Cloud Services Module for Codomyrmex.

This module provides integrations with various cloud service APIs including:
- Coda.io: Document and database API for Coda docs
- AWS: Amazon Web Services (S3)
- GCP: Google Cloud Platform (GCS)
- Azure: Microsoft Azure (Blob Storage)
- Infomaniak: OpenStack-based public cloud (Compute, Storage, Network, DNS, etc.)

The module is organized into submodules for each cloud service:
- coda_io: Coda.io REST API v1 client
- aws: AWS S3 client
- gcp: GCP Storage client
- azure: Azure Blob client
- infomaniak: Infomaniak Public Cloud clients (Nova, Cinder, Neutron, Swift, S3, Keystone, Designate, Heat)
- common: Shared cloud utilities

Usage:
    from codomyrmex.cloud import CodaClient

    client = CodaClient(api_token="your-api-token")
    docs = client.list_docs()


Submodules:
    common: Shared cloud utilities."""

# Shared schemas for cross-module interop
import contextlib

with contextlib.suppress(ImportError):
    from codomyrmex.validation.schemas import Result, ResultStatus

# Import from coda_io submodule
import contextlib

from .coda_io import (
    ACLSettings,
    CellEdit,
    # Exceptions
    CodaAPIError,
    CodaAuthenticationError,
    # Client
    CodaClient,
    CodaForbiddenError,
    CodaGoneError,
    CodaNotFoundError,
    CodaRateLimitError,
    CodaValidationError,
    Column,
    ColumnList,
    Control,
    ControlList,
    # Models
    Doc,
    DocList,
    DocSize,
    FolderReference,
    Formula,
    FormulaList,
    Icon,
    Page,
    PageList,
    PageReference,
    Permission,
    PermissionList,
    Row,
    RowEdit,
    RowList,
    SharingMetadata,
    Table,
    TableList,
    TableReference,
    User,
    WorkspaceReference,
)

# Import from other submodules with optional dependencies
with contextlib.suppress(ImportError):
    from .aws import S3Client

with contextlib.suppress(ImportError):
    from .gcp import GCSClient

with contextlib.suppress(ImportError):
    from .azure import AzureBlobClient

# Infomaniak clients (requires openstacksdk and/or boto3)
try:
    from .infomaniak import (
        InfomaniakComputeClient,
        InfomaniakCredentials,
        InfomaniakDNSClient,
        InfomaniakHeatClient,
        InfomaniakIdentityClient,
        InfomaniakMeteringClient,
        InfomaniakNetworkClient,
        InfomaniakNewsletterClient,
        InfomaniakObjectStorageClient,
        InfomaniakS3Client,
        InfomaniakS3Credentials,
        InfomaniakVolumeClient,
        create_openstack_connection,
        create_s3_client,
    )
except ImportError:
    # openstacksdk not installed
    pass

# New submodule exports
from . import common


def cli_commands():
    """Return CLI commands for the cloud module."""

    def _list_providers():
        """List cloud providers."""
        print("Cloud Providers:")
        print("  coda_io     - Coda.io REST API v1 (always available)")
        print(
            f"  aws         - Amazon Web Services S3 ({'available' if S3Client else 'unavailable - install boto3'})"
        )
        print(
            f"  gcp         - Google Cloud Storage ({'available' if GCSClient else 'unavailable - install google-cloud-storage'})"
        )
        print(
            f"  azure       - Azure Blob Storage ({'available' if AzureBlobClient else 'unavailable - install azure-storage-blob'})"
        )
        print(
            f"  infomaniak  - Infomaniak Public Cloud ({'available' if InfomaniakComputeClient else 'unavailable - install openstacksdk'})"
        )

    def _cloud_status():
        """Show cloud status."""
        print("Cloud Module Status:")
        available = ["coda_io"]
        if S3Client:
            available.append("aws")
        if GCSClient:
            available.append("gcp")
        if AzureBlobClient:
            available.append("azure")
        if InfomaniakComputeClient:
            available.append("infomaniak")
        print(f"  Available providers: {', '.join(available)}")
        print(f"  Total providers: {len(available)}/5")

    return {
        "providers": _list_providers,
        "status": _cloud_status,
    }


__all__ = [
    "ACLSettings",
    "AzureBlobClient",
    "CellEdit",
    # Exceptions
    "CodaAPIError",
    "CodaAuthenticationError",
    # Client
    "CodaClient",
    "CodaForbiddenError",
    "CodaGoneError",
    "CodaNotFoundError",
    "CodaRateLimitError",
    "CodaValidationError",
    "Column",
    "ColumnList",
    "Control",
    "ControlList",
    # Models
    "Doc",
    "DocList",
    "DocSize",
    "FolderReference",
    "Formula",
    "FormulaList",
    "GCSClient",
    "Icon",
    # Infomaniak Clients
    "InfomaniakComputeClient",
    "InfomaniakCredentials",
    "InfomaniakDNSClient",
    "InfomaniakHeatClient",
    "InfomaniakIdentityClient",
    "InfomaniakMeteringClient",
    "InfomaniakNetworkClient",
    "InfomaniakNewsletterClient",
    "InfomaniakObjectStorageClient",
    "InfomaniakS3Client",
    "InfomaniakS3Credentials",
    "InfomaniakVolumeClient",
    "Page",
    "PageList",
    "PageReference",
    "Permission",
    "PermissionList",
    "Row",
    "RowEdit",
    "RowList",
    # Other Clients
    "S3Client",
    "SharingMetadata",
    "Table",
    "TableList",
    "TableReference",
    "User",
    "WorkspaceReference",
    "cli_commands",
    # Submodules
    "common",
    "create_openstack_connection",
    "create_s3_client",
]
