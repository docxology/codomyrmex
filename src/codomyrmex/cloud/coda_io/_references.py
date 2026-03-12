"""Reference types for Coda.io data models."""

from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class Icon:
    """Icon information."""

    name: str | None = None
    type: str | None = None
    browser_link: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> Optional["Icon"]:

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

        if not data:
            return None
        return cls(
            id=data.get("id", ""),
            type=data.get("type", "column"),
            href=data.get("href"),
        )
