"""Document and page models for Coda.io."""

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from ._helpers import _parse_datetime
from ._references import (
    DocSize,
    FolderReference,
    Icon,
    Image,
    PageReference,
    WorkspaceReference,
)


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
    def from_dict(cls, data: dict[str, Any] | None) -> "PersonValue | None":

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

        children_data = data.get("children", [])
        children = [PageReference.from_dict(c) for c in children_data if c]

        authors_data = data.get("authors", [])
        authors = (
            [PersonValue.from_dict(a) for a in authors_data if a]
            if authors_data
            else None
        )

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
            authors=[a for a in authors if a is not None] if authors else None,
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

        return cls(
            id=data.get("id", ""),
            type=data.get("type", ""),
            text=data.get("text"),
        )
