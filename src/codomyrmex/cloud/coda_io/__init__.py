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
    "ACLSettings",
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
    # Core resources
    "Doc",
    "DocList",
    "DocSize",
    "FolderReference",
    "Formula",
    "FormulaList",
    "Icon",
    "InsertRowsResult",
    # Mutations
    "MutationStatus",
    "Page",
    "PageContentItem",
    "PageList",
    "PageReference",
    # Permissions
    "Permission",
    "PermissionList",
    "Principal",
    "Row",
    "RowEdit",
    "RowList",
    "SharingMetadata",
    "Table",
    "TableList",
    "TableReference",
    # User
    "User",
    # References
    "WorkspaceReference",
]
