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
from .models import (
    # Core resources
    Doc,
    DocList,
    Page,
    PageList,
    PageReference,
    PageContentItem,
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
    # Permissions
    Permission,
    PermissionList,
    SharingMetadata,
    ACLSettings,
    Principal,
    # References
    WorkspaceReference,
    FolderReference,
    Icon,
    DocSize,
    # User
    User,
    # Mutations
    MutationStatus,
    InsertRowsResult,
)
from .exceptions import (
    CodaAPIError,
    CodaAuthenticationError,
    CodaForbiddenError,
    CodaNotFoundError,
    CodaRateLimitError,
    CodaValidationError,
    CodaGoneError,
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
