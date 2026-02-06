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
"""

# Import from coda_io submodule
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
try:
    from .aws import S3Client
except ImportError:
    S3Client = None  # boto3 not installed

try:
    from .gcp import GCSClient
except ImportError:
    GCSClient = None  # google-cloud-storage not installed

try:
    from .azure import AzureBlobClient
except ImportError:
    AzureBlobClient = None  # azure-storage-blob not installed

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
    InfomaniakComputeClient = None
    InfomaniakVolumeClient = None
    InfomaniakNetworkClient = None
    InfomaniakObjectStorageClient = None
    InfomaniakS3Client = None
    InfomaniakIdentityClient = None
    InfomaniakDNSClient = None
    InfomaniakHeatClient = None
    InfomaniakMeteringClient = None
    InfomaniakNewsletterClient = None
    InfomaniakCredentials = None
    InfomaniakS3Credentials = None
    create_openstack_connection = None
    create_s3_client = None

# New submodule exports
from . import common

__all__ = [
    # Client
    "CodaClient",
    # Models
    "Doc",
    "DocList",
    "Page",
    "PageList",
    "PageReference",
    "Table",
    "TableList",
    "TableReference",
    "Column",
    "ColumnList",
    "Row",
    "RowList",
    "RowEdit",
    "CellEdit",
    "Formula",
    "FormulaList",
    "Control",
    "ControlList",
    "Permission",
    "PermissionList",
    "SharingMetadata",
    "ACLSettings",
    "User",
    "WorkspaceReference",
    "FolderReference",
    "Icon",
    "DocSize",
    # Exceptions
    "CodaAPIError",
    "CodaAuthenticationError",
    "CodaForbiddenError",
    "CodaNotFoundError",
    "CodaRateLimitError",
    "CodaValidationError",
    "CodaGoneError",
    # Other Clients
    "S3Client",
    "GCSClient",
    "AzureBlobClient",
    # Infomaniak Clients
    "InfomaniakComputeClient",
    "InfomaniakVolumeClient",
    "InfomaniakNetworkClient",
    "InfomaniakObjectStorageClient",
    "InfomaniakS3Client",
    "InfomaniakIdentityClient",
    "InfomaniakDNSClient",
    "InfomaniakHeatClient",
    "InfomaniakMeteringClient",
    "InfomaniakNewsletterClient",
    "InfomaniakCredentials",
    "InfomaniakS3Credentials",
    "create_openstack_connection",
    "create_s3_client",
    # Submodules
    "common",
]

