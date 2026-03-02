from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Optional

from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)
"""
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
    name: str | None = None
    type: str | None = None
    browser_link: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> Optional["Icon"]:
        """from Dict ."""

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
    browser_link: str | None = None
    type: str | None = None
    width: int | None = None
    height: int | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> Optional["Image"]:
        """from Dict ."""

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
    name: str | None = None
    organization_id: str | None = None
    browser_link: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> Optional["WorkspaceReference"]:
        """from Dict ."""

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
    name: str | None = None
    browser_link: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> Optional["FolderReference"]:
        """from Dict ."""

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
    def from_dict(cls, data: dict[str, Any] | None) -> Optional["DocSize"]:
        """from Dict ."""

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
    href: str | None = None
    browser_link: str | None = None
    name: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> Optional["PageReference"]:
        """from Dict ."""

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
    table_type: str | None = None
    href: str | None = None
    browser_link: str | None = None
    name: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> Optional["TableReference"]:
        """from Dict ."""

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
    href: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> Optional["ColumnReference"]:
        """from Dict ."""

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
    created_at: datetime | None = None
    updated_at: datetime | None = None
    workspace: WorkspaceReference | None = None
    folder: FolderReference | None = None
    workspace_id: str | None = None  # Deprecated
    folder_id: str | None = None  # Deprecated
    icon: Icon | None = None
    doc_size: DocSize | None = None
    source_doc: dict[str, Any] | None = None
    published: dict[str, Any] | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Doc":
        """from Dict ."""

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
    items: list[Doc]
    href: str | None = None
    next_page_token: str | None = None
    next_page_link: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "DocList":
        """from Dict ."""

        return cls(
            items=[Doc.from_dict(item) for item in data.get("items", [])],
            href=data.get("href"),
            next_page_token=data.get("nextPageToken"),
            next_page_link=data.get("nextPageLink"),
        )


@dataclass
class PersonValue:
    """A person reference."""
    name: str | None = None
    email: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> Optional["PersonValue"]:
        """from Dict ."""

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
    children: list[PageReference]
    content_type: str
    subtitle: str | None = None
    icon: Icon | None = None
    image: Image | None = None
    parent: PageReference | None = None
    authors: list[PersonValue] | None = None
    created_at: datetime | None = None
    created_by: PersonValue | None = None
    updated_at: datetime | None = None
    updated_by: PersonValue | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Page":
        """from Dict ."""

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
    items: list[Page]
    href: str | None = None
    next_page_token: str | None = None
    next_page_link: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PageList":
        """from Dict ."""

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
    text: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PageContentItem":
        """from Dict ."""

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
    def from_dict(cls, data: dict[str, Any]) -> "Sort":
        """from Dict ."""

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
    created_at: datetime | None = None
    updated_at: datetime | None = None
    parent: PageReference | None = None
    parent_table: TableReference | None = None
    display_column: ColumnReference | None = None
    sorts: list[Sort] | None = None
    filter: dict[str, Any] | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Table":
        """from Dict ."""

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
    items: list[Table]
    href: str | None = None
    next_page_token: str | None = None
    next_page_link: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TableList":
        """from Dict ."""

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
    format: dict[str, Any]
    display: bool = False
    calculated: bool = False
    formula: str | None = None
    default_value: str | None = None
    parent: TableReference | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Column":
        """from Dict ."""

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
    items: list[Column]
    href: str | None = None
    next_page_token: str | None = None
    next_page_link: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ColumnList":
        """from Dict ."""

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
    values: dict[str, Any]
    created_at: datetime | None = None
    updated_at: datetime | None = None
    parent: TableReference | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Row":
        """from Dict ."""

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
    items: list[Row]
    href: str | None = None
    next_page_token: str | None = None
    next_page_link: str | None = None
    next_sync_token: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "RowList":
        """from Dict ."""

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

    def to_dict(self) -> dict[str, Any]:
        """Return a dictionary representation of this object."""
        return {
            "column": self.column,
            "value": self.value,
        }


@dataclass
class RowEdit:
    """A row edit with cell values."""
    cells: list[CellEdit]

    def to_dict(self) -> dict[str, Any]:
        """Return a dictionary representation of this object."""
        return {"cells": [cell.to_dict() for cell in self.cells]}


@dataclass
class Formula:
    """A named formula in a Coda doc."""
    id: str
    type: str
    href: str
    name: str
    value: Any
    parent: PageReference | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Formula":
        """from Dict ."""
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
    items: list[Formula]
    href: str | None = None
    next_page_token: str | None = None
    next_page_link: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "FormulaList":
        """from Dict ."""

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
    parent: PageReference | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Control":
        """from Dict ."""

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
    items: list[Control]
    href: str | None = None
    next_page_token: str | None = None
    next_page_link: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ControlList":
        """from Dict ."""

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
    email: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Principal":
        """from Dict ."""

        return cls(
            type=data.get("type", ""),
            email=data.get("email"),
        )

    def to_dict(self) -> dict[str, Any]:
        """Return a dictionary representation of this object."""

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
    def from_dict(cls, data: dict[str, Any]) -> "Permission":
        """from Dict ."""

        return cls(
            id=data.get("id", ""),
            principal=Principal.from_dict(data.get("principal", {})),
            access=data.get("access", ""),
        )


@dataclass
class PermissionList:
    """List of permissions with pagination."""
    items: list[Permission]
    href: str
    next_page_token: str | None = None
    next_page_link: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PermissionList":
        """from Dict ."""

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
    def from_dict(cls, data: dict[str, Any]) -> "SharingMetadata":
        """from Dict ."""

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
    def from_dict(cls, data: dict[str, Any]) -> "ACLSettings":
        """from Dict ."""

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
    workspace: WorkspaceReference | None = None
    picture_link: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "User":
        """from Dict ."""

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
    warning: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "MutationStatus":
        """from Dict ."""

        return cls(
            completed=data.get("completed", False),
            warning=data.get("warning"),
        )


@dataclass
class InsertRowsResult:
    """Result of inserting rows."""
    request_id: str
    added_row_ids: list[str] | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "InsertRowsResult":
        """from Dict ."""
        return cls(
            request_id=data.get("requestId", ""),
            added_row_ids=data.get("addedRowIds"),
        )


# ============================================================================
# Helpers
# ============================================================================

def _parse_datetime(value: str | None) -> datetime | None:
    """Parse ISO 8601 datetime string."""
    if not value:
        return None
    try:
        # Handle various ISO 8601 formats
        if value.endswith("Z"):
            value = value[:-1] + "+00:00"
        return datetime.fromisoformat(value)
    except (ValueError, TypeError) as e:
        logger.debug("Failed to parse datetime %r: %s", value, e)
        return None
