"""
Coda.io API Client Submodule.

This submodule provides a comprehensive Python client for the Coda.io REST API v1,
enabling programmatic access to Coda docs, pages, tables, rows, and more.

Usage:
    from codomyrmex.cloud.coda_io import CodaClient

    client = CodaClient(api_token="your-api-token")
    docs = client.list_docs()
"""

from .client import CodaClient
from .exceptions import (
    CodaAPIError,
    CodaAuthenticationError,
    CodaForbiddenError,
    CodaGoneError,
    CodaNotFoundError,
    CodaRateLimitError,
    CodaValidationError,
)
from .models import (
    ACLSettings,
    CellEdit,
    Column,
    ColumnList,
    Control,
    ControlList,
    # Core resources
    Doc,
    DocList,
    DocSize,
    FolderReference,
    Formula,
    FormulaList,
    Icon,
    InsertRowsResult,
    # Mutations
    MutationStatus,
    Page,
    PageContentItem,
    PageList,
    PageReference,
    # Permissions
    Permission,
    PermissionList,
    Principal,
    Row,
    RowEdit,
    RowList,
    SharingMetadata,
    Table,
    TableList,
    TableReference,
    # User
    User,
    # References
    WorkspaceReference,
)

__all__ = [
    # Client
    "CodaClient",
    # Core resources
    "Doc",
    "DocList",
    "Page",
    "PageList",
    "PageReference",
    "PageContentItem",
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
    # Permissions
    "Permission",
    "PermissionList",
    "SharingMetadata",
    "ACLSettings",
    "Principal",
    # References
    "WorkspaceReference",
    "FolderReference",
    "Icon",
    "DocSize",
    # User
    "User",
    # Mutations
    "MutationStatus",
    "InsertRowsResult",
    # Exceptions
    "CodaAPIError",
    "CodaAuthenticationError",
    "CodaForbiddenError",
    "CodaNotFoundError",
    "CodaRateLimitError",
    "CodaValidationError",
    "CodaGoneError",
]
