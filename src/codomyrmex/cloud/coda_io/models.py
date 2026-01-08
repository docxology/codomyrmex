from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from dataclasses import dataclass, field
from enum import Enum

from codomyrmex.logging_monitoring import get_logger




























































"""
"""Core functionality module

This module provides models functionality including:
- 37 functions: _parse_datetime, from_dict, from_dict...
- 41 classes: TableType, PageType, ControlType...

Usage:
    # Example usage here
"""
logger = get_logger(__name__)
Data models for Coda.io API resources.

These dataclasses represent the JSON responses from the Coda API v1,
providing type-safe access to API data with automatic deserialization.
"""



# ============================================================================
# Enums
# ============================================================================

class TableType(Enum):
    """Type of table in Coda."""
    TABLE = "table"
    VIEW = "view"


class PageType(Enum):
    """Type of page content."""
    CANVAS = "canvas"
    EMBED = "embed"
    SYNC_PAGE = "syncPage"


class ControlType(Enum):
    """Type of control widget."""
    AI_BLOCK = "aiBlock"
    BUTTON = "button"
    CHECKBOX = "checkbox"
    DATE_PICKER = "datePicker"
    DATE_RANGE_PICKER = "dateRangePicker"
    DATE_TIME_PICKER = "dateTimePicker"
    LOOKUP = "lookup"
    MULTISELECT = "multiselect"
    SELECT = "select"
    SCALE = "scale"
    SLIDER = "slider"
    REACTION = "reaction"
    TEXTBOX = "textbox"
    TIME_PICKER = "timePicker"


class AccessType(Enum):
    """Permission access level."""
    NONE = "none"
    READONLY = "readonly"
    WRITE = "write"
    COMMENT = "comment"


class DocPublishMode(Enum):
    """Publishing mode for docs."""
    VIEW = "view"
    PLAY = "play"
    EDIT = "edit"


class ValueFormat(Enum):
    """Format for cell values."""
    SIMPLE = "simple"
    SIMPLE_WITH_ARRAYS = "simpleWithArrays"
    RICH = "rich"


# ============================================================================
# Reference Types
# ============================================================================

@dataclass
class Icon:
    """Icon information."""
    name: Optional[str] = None
    type: Optional[str] = None
    browser_link: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> Optional["Icon"]:
    """Brief description of from_dict.

Args:
    cls : Description of cls
    data : Description of data

    Returns: Description of return value (type: Any)
"""
        if not data:
            return None
        return cls(
            name=data.get("name"),
            type=data.get("type"),
            browser_link=data.get("browserLink"),
        )


@dataclass
class Image:
    """Image information."""
    browser_link: Optional[str] = None
    type: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    
    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> Optional["Image"]:
    """Brief description of from_dict.

Args:
    cls : Description of cls
    data : Description of data

    Returns: Description of return value (type: Any)
"""
        if not data:
            return None
        return cls(
            browser_link=data.get("browserLink"),
            type=data.get("type"),
            width=data.get("width"),
            height=data.get("height"),
        )


@dataclass
class WorkspaceReference:
    """Reference to a Coda workspace."""
    id: str
    type: str = "workspace"
    name: Optional[str] = None
    organization_id: Optional[str] = None
    browser_link: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> Optional["WorkspaceReference"]:
    """Brief description of from_dict.

Args:
    cls : Description of cls
    data : Description of data

    Returns: Description of return value (type: Any)
"""
        if not data:
            return None
        return cls(
            id=data.get("id", ""),
            type=data.get("type", "workspace"),
            name=data.get("name"),
            organization_id=data.get("organizationId"),
            browser_link=data.get("browserLink"),
        )


@dataclass
class FolderReference:
    """Reference to a Coda folder."""
    id: str
    type: str = "folder"
    name: Optional[str] = None
    browser_link: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> Optional["FolderReference"]:
    """Brief description of from_dict.

Args:
    cls : Description of cls
    data : Description of data

    Returns: Description of return value (type: Any)
"""
        if not data:
            return None
        return cls(
            id=data.get("id", ""),
            type=data.get("type", "folder"),
            name=data.get("name"),
            browser_link=data.get("browserLink"),
        )


@dataclass
class DocSize:
    """Size information for a doc."""
    total_row_count: int = 0
    table_and_view_count: int = 0
    page_count: int = 0
    over_api_size_limit: bool = False
    
    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> Optional["DocSize"]:
    """Brief description of from_dict.

Args:
    cls : Description of cls
    data : Description of data

    Returns: Description of return value (type: Any)
"""
        if not data:
            return None
        return cls(
            total_row_count=data.get("totalRowCount", 0),
            table_and_view_count=data.get("tableAndViewCount", 0),
            page_count=data.get("pageCount", 0),
            over_api_size_limit=data.get("overApiSizeLimit", False),
        )


@dataclass
class PageReference:
    """Reference to a page."""
    id: str
    type: str = "page"
    href: Optional[str] = None
    browser_link: Optional[str] = None
    name: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> Optional["PageReference"]:
    """Brief description of from_dict.

Args:
    cls : Description of cls
    data : Description of data

    Returns: Description of return value (type: Any)
"""
        if not data:
            return None
        return cls(
            id=data.get("id", ""),
            type=data.get("type", "page"),
            href=data.get("href"),
            browser_link=data.get("browserLink"),
            name=data.get("name"),
        )


@dataclass
class TableReference:
    """Reference to a table."""
    id: str
    type: str = "table"
    table_type: Optional[str] = None
    href: Optional[str] = None
    browser_link: Optional[str] = None
    name: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> Optional["TableReference"]:
    """Brief description of from_dict.

Args:
    cls : Description of cls
    data : Description of data

    Returns: Description of return value (type: Any)
"""
        if not data:
            return None
        return cls(
            id=data.get("id", ""),
            type=data.get("type", "table"),
            table_type=data.get("tableType"),
            href=data.get("href"),
            browser_link=data.get("browserLink"),
            name=data.get("name"),
        )


@dataclass
class ColumnReference:
    """Reference to a column."""
    id: str
    type: str = "column"
    href: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> Optional["ColumnReference"]:
    """Brief description of from_dict.

Args:
    cls : Description of cls
    data : Description of data

    Returns: Description of return value (type: Any)
"""
        if not data:
            return None
        return cls(
            id=data.get("id", ""),
            type=data.get("type", "column"),
            href=data.get("href"),
        )


# ============================================================================
# Core Resources
# ============================================================================

@dataclass
class Doc:
    """A Coda document."""
    id: str
    type: str
    href: str
    browser_link: str
    name: str
    owner: str
    owner_name: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    workspace: Optional[WorkspaceReference] = None
    folder: Optional[FolderReference] = None
    workspace_id: Optional[str] = None  # Deprecated
    folder_id: Optional[str] = None  # Deprecated
    icon: Optional[Icon] = None
    doc_size: Optional[DocSize] = None
    source_doc: Optional[Dict[str, Any]] = None
    published: Optional[Dict[str, Any]] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Doc":
    """Brief description of from_dict.

Args:
    cls : Description of cls
    data : Description of data

    Returns: Description of return value (type: str)
"""
        return cls(
            id=data.get("id", ""),
            type=data.get("type", "doc"),
            href=data.get("href", ""),
            browser_link=data.get("browserLink", ""),
            name=data.get("name", ""),
            owner=data.get("owner", ""),
            owner_name=data.get("ownerName", ""),
            created_at=_parse_datetime(data.get("createdAt")),
            updated_at=_parse_datetime(data.get("updatedAt")),
            workspace=WorkspaceReference.from_dict(data.get("workspace")),
            folder=FolderReference.from_dict(data.get("folder")),
            workspace_id=data.get("workspaceId"),
            folder_id=data.get("folderId"),
            icon=Icon.from_dict(data.get("icon")),
            doc_size=DocSize.from_dict(data.get("docSize")),
            source_doc=data.get("sourceDoc"),
            published=data.get("published"),
        )


@dataclass
class DocList:
    """List of docs with pagination."""
    items: List[Doc]
    href: Optional[str] = None
    next_page_token: Optional[str] = None
    next_page_link: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DocList":
    """Brief description of from_dict.

Args:
    cls : Description of cls
    data : Description of data

    Returns: Description of return value (type: str)
"""
        return cls(
            items=[Doc.from_dict(item) for item in data.get("items", [])],
            href=data.get("href"),
            next_page_token=data.get("nextPageToken"),
            next_page_link=data.get("nextPageLink"),
        )


@dataclass
class PersonValue:
    """A person reference."""
    name: Optional[str] = None
    email: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> Optional["PersonValue"]:
    """Brief description of from_dict.

Args:
    cls : Description of cls
    data : Description of data

    Returns: Description of return value (type: Any)
"""
        if not data:
            return None
        return cls(
            name=data.get("name"),
            email=data.get("email"),
        )


@dataclass
class Page:
    """A page in a Coda doc."""
    id: str
    type: str
    href: str
    name: str
    is_hidden: bool
    is_effectively_hidden: bool
    browser_link: str
    children: List[PageReference]
    content_type: str
    subtitle: Optional[str] = None
    icon: Optional[Icon] = None
    image: Optional[Image] = None
    parent: Optional[PageReference] = None
    authors: Optional[List[PersonValue]] = None
    created_at: Optional[datetime] = None
    created_by: Optional[PersonValue] = None
    updated_at: Optional[datetime] = None
    updated_by: Optional[PersonValue] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Page":
    """Brief description of from_dict.

Args:
    cls : Description of cls
    data : Description of data

    Returns: Description of return value (type: str)
"""
        children_data = data.get("children", [])
        children = [PageReference.from_dict(c) for c in children_data if c]
        
        authors_data = data.get("authors", [])
        authors = [PersonValue.from_dict(a) for a in authors_data if a] if authors_data else None
        
        return cls(
            id=data.get("id", ""),
            type=data.get("type", "page"),
            href=data.get("href", ""),
            name=data.get("name", ""),
            is_hidden=data.get("isHidden", False),
            is_effectively_hidden=data.get("isEffectivelyHidden", False),
            browser_link=data.get("browserLink", ""),
            children=[c for c in children if c is not None],
            content_type=data.get("contentType", "canvas"),
            subtitle=data.get("subtitle"),
            icon=Icon.from_dict(data.get("icon")),
            image=Image.from_dict(data.get("image")),
            parent=PageReference.from_dict(data.get("parent")),
            authors=authors,
            created_at=_parse_datetime(data.get("createdAt")),
            created_by=PersonValue.from_dict(data.get("createdBy")),
            updated_at=_parse_datetime(data.get("updatedAt")),
            updated_by=PersonValue.from_dict(data.get("updatedBy")),
        )


@dataclass
class PageList:
    """List of pages with pagination."""
    items: List[Page]
    href: Optional[str] = None
    next_page_token: Optional[str] = None
    next_page_link: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PageList":
    """Brief description of from_dict.

Args:
    cls : Description of cls
    data : Description of data

    Returns: Description of return value (type: str)
"""
        return cls(
            items=[Page.from_dict(item) for item in data.get("items", [])],
            href=data.get("href"),
            next_page_token=data.get("nextPageToken"),
            next_page_link=data.get("nextPageLink"),
        )


@dataclass
class PageContentItem:
    """A content item within a page."""
    id: str
    type: str
    text: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PageContentItem":
    """Brief description of from_dict.

Args:
    cls : Description of cls
    data : Description of data

    Returns: Description of return value (type: str)
"""
        return cls(
            id=data.get("id", ""),
            type=data.get("type", ""),
            text=data.get("text"),
        )


@dataclass
class Sort:
    """Sort configuration for a table."""
    column: ColumnReference
    direction: str  # "ascending" or "descending"
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Sort":
    """Brief description of from_dict.

Args:
    cls : Description of cls
    data : Description of data

    Returns: Description of return value (type: str)
"""
        return cls(
            column=ColumnReference.from_dict(data.get("column")) or ColumnReference(id=""),
            direction=data.get("direction", "ascending"),
        )


@dataclass
class Table:
    """A table in a Coda doc."""
    id: str
    type: str
    table_type: str
    href: str
    name: str
    browser_link: str
    row_count: int
    layout: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    parent: Optional[PageReference] = None
    parent_table: Optional[TableReference] = None
    display_column: Optional[ColumnReference] = None
    sorts: Optional[List[Sort]] = None
    filter: Optional[Dict[str, Any]] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Table":
    """Brief description of from_dict.

Args:
    cls : Description of cls
    data : Description of data

    Returns: Description of return value (type: str)
"""
        sorts_data = data.get("sorts", [])
        sorts = [Sort.from_dict(s) for s in sorts_data] if sorts_data else None
        
        return cls(
            id=data.get("id", ""),
            type=data.get("type", "table"),
            table_type=data.get("tableType", "table"),
            href=data.get("href", ""),
            name=data.get("name", ""),
            browser_link=data.get("browserLink", ""),
            row_count=data.get("rowCount", 0),
            layout=data.get("layout", "default"),
            created_at=_parse_datetime(data.get("createdAt")),
            updated_at=_parse_datetime(data.get("updatedAt")),
            parent=PageReference.from_dict(data.get("parent")),
            parent_table=TableReference.from_dict(data.get("parentTable")),
            display_column=ColumnReference.from_dict(data.get("displayColumn")),
            sorts=sorts,
            filter=data.get("filter"),
        )


@dataclass
class TableList:
    """List of tables with pagination."""
    items: List[Table]
    href: Optional[str] = None
    next_page_token: Optional[str] = None
    next_page_link: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TableList":
    """Brief description of from_dict.

Args:
    cls : Description of cls
    data : Description of data

    Returns: Description of return value (type: str)
"""
        return cls(
            items=[Table.from_dict(item) for item in data.get("items", [])],
            href=data.get("href"),
            next_page_token=data.get("nextPageToken"),
            next_page_link=data.get("nextPageLink"),
        )


@dataclass
class Column:
    """A column in a Coda table."""
    id: str
    type: str
    href: str
    name: str
    format: Dict[str, Any]
    display: bool = False
    calculated: bool = False
    formula: Optional[str] = None
    default_value: Optional[str] = None
    parent: Optional[TableReference] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Column":
    """Brief description of from_dict.

Args:
    cls : Description of cls
    data : Description of data

    Returns: Description of return value (type: str)
"""
        return cls(
            id=data.get("id", ""),
            type=data.get("type", "column"),
            href=data.get("href", ""),
            name=data.get("name", ""),
            format=data.get("format", {}),
            display=data.get("display", False),
            calculated=data.get("calculated", False),
            formula=data.get("formula"),
            default_value=data.get("defaultValue"),
            parent=TableReference.from_dict(data.get("parent")),
        )


@dataclass
class ColumnList:
    """List of columns with pagination."""
    items: List[Column]
    href: Optional[str] = None
    next_page_token: Optional[str] = None
    next_page_link: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ColumnList":
    """Brief description of from_dict.

Args:
    cls : Description of cls
    data : Description of data

    Returns: Description of return value (type: str)
"""
        return cls(
            items=[Column.from_dict(item) for item in data.get("items", [])],
            href=data.get("href"),
            next_page_token=data.get("nextPageToken"),
            next_page_link=data.get("nextPageLink"),
        )


@dataclass
class Row:
    """A row in a Coda table."""
    id: str
    type: str
    href: str
    name: str
    index: int
    browser_link: str
    values: Dict[str, Any]
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    parent: Optional[TableReference] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Row":
    """Brief description of from_dict.

Args:
    cls : Description of cls
    data : Description of data

    Returns: Description of return value (type: str)
"""
        return cls(
            id=data.get("id", ""),
            type=data.get("type", "row"),
            href=data.get("href", ""),
            name=data.get("name", ""),
            index=data.get("index", 0),
            browser_link=data.get("browserLink", ""),
            values=data.get("values", {}),
            created_at=_parse_datetime(data.get("createdAt")),
            updated_at=_parse_datetime(data.get("updatedAt")),
            parent=TableReference.from_dict(data.get("parent")),
        )


@dataclass
class RowList:
    """List of rows with pagination."""
    items: List[Row]
    href: Optional[str] = None
    next_page_token: Optional[str] = None
    next_page_link: Optional[str] = None
    next_sync_token: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RowList":
    """Brief description of from_dict.

Args:
    cls : Description of cls
    data : Description of data

    Returns: Description of return value (type: str)
"""
        return cls(
            items=[Row.from_dict(item) for item in data.get("items", [])],
            href=data.get("href"),
            next_page_token=data.get("nextPageToken"),
            next_page_link=data.get("nextPageLink"),
            next_sync_token=data.get("nextSyncToken"),
        )


@dataclass
class CellEdit:
    """A cell value edit."""
    column: str  # Column ID or name
    value: Any
    
    def to_dict(self) -> Dict[str, Any]:
    """Brief description of to_dict.

Args:
    self : Description of self

    Returns: Description of return value (type: Any)
"""
    """Brief description of to_dict.

Args:
    self : Description of self

    Returns: Description of return value (type: Any)
"""
        return {"column": self.column, "value": self.value}


@dataclass
class RowEdit:
    """A row edit with cell values."""
    cells: List[CellEdit]
    
    def to_dict(self) -> Dict[str, Any]:
        return {"cells": [cell.to_dict() for cell in self.cells]}


@dataclass
class Formula:
    """A named formula in a Coda doc."""
    id: str
    type: str
    href: str
    name: str
    value: Any
    parent: Optional[PageReference] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Formula":
    """Brief description of from_dict.

Args:
    cls : Description of cls
    data : Description of data

    Returns: Description of return value (type: str)
"""
    """Brief description of from_dict.

Args:
    cls : Description of cls
    data : Description of data

    Returns: Description of return value (type: str)
"""
        return cls(
            id=data.get("id", ""),
            type=data.get("type", "formula"),
            href=data.get("href", ""),
            name=data.get("name", ""),
            value=data.get("value"),
            parent=PageReference.from_dict(data.get("parent")),
        )


@dataclass
class FormulaList:
    """List of formulas with pagination."""
    items: List[Formula]
    href: Optional[str] = None
    next_page_token: Optional[str] = None
    next_page_link: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FormulaList":
    """Brief description of from_dict.

Args:
    cls : Description of cls
    data : Description of data

    Returns: Description of return value (type: str)
"""
        return cls(
            items=[Formula.from_dict(item) for item in data.get("items", [])],
            href=data.get("href"),
            next_page_token=data.get("nextPageToken"),
            next_page_link=data.get("nextPageLink"),
        )


@dataclass
class Control:
    """A control in a Coda doc."""
    id: str
    type: str
    href: str
    name: str
    control_type: str
    value: Any
    parent: Optional[PageReference] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Control":
    """Brief description of from_dict.

Args:
    cls : Description of cls
    data : Description of data

    Returns: Description of return value (type: str)
"""
        return cls(
            id=data.get("id", ""),
            type=data.get("type", "control"),
            href=data.get("href", ""),
            name=data.get("name", ""),
            control_type=data.get("controlType", ""),
            value=data.get("value"),
            parent=PageReference.from_dict(data.get("parent")),
        )


@dataclass
class ControlList:
    """List of controls with pagination."""
    items: List[Control]
    href: Optional[str] = None
    next_page_token: Optional[str] = None
    next_page_link: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ControlList":
    """Brief description of from_dict.

Args:
    cls : Description of cls
    data : Description of data

    Returns: Description of return value (type: str)
"""
        return cls(
            items=[Control.from_dict(item) for item in data.get("items", [])],
            href=data.get("href"),
            next_page_token=data.get("nextPageToken"),
            next_page_link=data.get("nextPageLink"),
        )


# ============================================================================
# Permissions
# ============================================================================

@dataclass
class Principal:
    """A principal (user or group) for permissions."""
    type: str  # "email", "domain", "anyone"
    email: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Principal":
    """Brief description of from_dict.

Args:
    cls : Description of cls
    data : Description of data

    Returns: Description of return value (type: str)
"""
        return cls(
            type=data.get("type", ""),
            email=data.get("email"),
        )
    
    def to_dict(self) -> Dict[str, Any]:
    """Brief description of to_dict.

Args:
    self : Description of self

    Returns: Description of return value (type: Any)
"""
        result = {"type": self.type}
        if self.email:
            result["email"] = self.email
        return result


@dataclass
class Permission:
    """A permission on a doc."""
    id: str
    principal: Principal
    access: str
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Permission":
    """Brief description of from_dict.

Args:
    cls : Description of cls
    data : Description of data

    Returns: Description of return value (type: str)
"""
        return cls(
            id=data.get("id", ""),
            principal=Principal.from_dict(data.get("principal", {})),
            access=data.get("access", ""),
        )


@dataclass
class PermissionList:
    """List of permissions with pagination."""
    items: List[Permission]
    href: str
    next_page_token: Optional[str] = None
    next_page_link: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PermissionList":
    """Brief description of from_dict.

Args:
    cls : Description of cls
    data : Description of data

    Returns: Description of return value (type: str)
"""
        return cls(
            items=[Permission.from_dict(item) for item in data.get("items", [])],
            href=data.get("href", ""),
            next_page_token=data.get("nextPageToken"),
            next_page_link=data.get("nextPageLink"),
        )


@dataclass
class SharingMetadata:
    """Sharing metadata for a doc."""
    can_share: bool
    can_share_with_workspace: bool
    can_share_with_org: bool
    can_copy: bool
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SharingMetadata":
    """Brief description of from_dict.

Args:
    cls : Description of cls
    data : Description of data

    Returns: Description of return value (type: str)
"""
        return cls(
            can_share=data.get("canShare", False),
            can_share_with_workspace=data.get("canShareWithWorkspace", False),
            can_share_with_org=data.get("canShareWithOrg", False),
            can_copy=data.get("canCopy", False),
        )


@dataclass
class ACLSettings:
    """ACL settings for a doc."""
    allow_editors_to_change_permissions: bool
    allow_copying: bool
    allow_viewers_to_request_editing: bool
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ACLSettings":
    """Brief description of from_dict.

Args:
    cls : Description of cls
    data : Description of data

    Returns: Description of return value (type: str)
"""
        return cls(
            allow_editors_to_change_permissions=data.get("allowEditorsToChangePermissions", False),
            allow_copying=data.get("allowCopying", False),
            allow_viewers_to_request_editing=data.get("allowViewersToRequestEditing", False),
        )


# ============================================================================
# User / Account
# ============================================================================

@dataclass
class User:
    """Current user information from whoami endpoint."""
    name: str
    login_id: str
    type: str
    scoped: bool
    token_name: str
    href: str
    workspace: Optional[WorkspaceReference] = None
    picture_link: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "User":
    """Brief description of from_dict.

Args:
    cls : Description of cls
    data : Description of data

    Returns: Description of return value (type: str)
"""
        return cls(
            name=data.get("name", ""),
            login_id=data.get("loginId", ""),
            type=data.get("type", "user"),
            scoped=data.get("scoped", False),
            token_name=data.get("tokenName", ""),
            href=data.get("href", ""),
            workspace=WorkspaceReference.from_dict(data.get("workspace")),
            picture_link=data.get("pictureLink"),
        )


# ============================================================================
# Mutation Results
# ============================================================================

@dataclass
class MutationStatus:
    """Status of an asynchronous mutation."""
    completed: bool
    warning: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MutationStatus":
    """Brief description of from_dict.

Args:
    cls : Description of cls
    data : Description of data

    Returns: Description of return value (type: str)
"""
        return cls(
            completed=data.get("completed", False),
            warning=data.get("warning"),
        )


@dataclass
class InsertRowsResult:
    """Result of inserting rows."""
    request_id: str
    added_row_ids: Optional[List[str]] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "InsertRowsResult":
        return cls(
            request_id=data.get("requestId", ""),
            added_row_ids=data.get("addedRowIds"),
        )


# ============================================================================
# Helpers
# ============================================================================

def _parse_datetime(value: Optional[str]) -> Optional[datetime]:
    """Parse ISO 8601 datetime string."""
    if not value:
        return None
    try:
        # Handle various ISO 8601 formats
        if value.endswith("Z"):
            value = value[:-1] + "+00:00"
        return datetime.fromisoformat(value)
    except (ValueError, TypeError):
        return None
