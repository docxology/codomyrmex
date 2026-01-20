"""
Cloud Services Module for Codomyrmex.

This module provides integrations with various cloud service APIs including:
- Coda.io: Document and database API for Coda docs
- AWS: Amazon Web Services (S3)
- GCP: Google Cloud Platform (GCS)
- Azure: Microsoft Azure (Blob Storage)

The module is organized into submodules for each cloud service:
- coda_io: Coda.io REST API v1 client
- aws: AWS S3 client
- gcp: GCP Storage client
- azure: Azure Blob client

Usage:
    from codomyrmex.cloud import CodaClient
    
    client = CodaClient(api_token="your-api-token")
    docs = client.list_docs()
"""

# Import from coda_io submodule
from .coda_io import (
    # Client
    CodaClient,
    # Models
    Doc,
    DocList,
    Page,
    PageList,
    PageReference,
    Table,
    TableList,
    TableReference,
    Column,
    ColumnList,
    Row,
    RowList,
    RowEdit,
    CellEdit,
    Formula,
    FormulaList,
    Control,
    ControlList,
    Permission,
    PermissionList,
    SharingMetadata,
    ACLSettings,
    User,
    WorkspaceReference,
    FolderReference,
    Icon,
    DocSize,
    # Exceptions
    CodaAPIError,
    CodaAuthenticationError,
    CodaForbiddenError,
    CodaNotFoundError,
    CodaRateLimitError,
    CodaValidationError,
    CodaGoneError,
)

# Import from other submodules
from .aws import S3Client
from .gcp import GCSClient
from .azure import AzureBlobClient

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
]
