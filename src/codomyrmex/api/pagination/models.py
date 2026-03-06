"""Pagination data models: enums, dataclasses, and abstract base class."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class PaginationStrategy(Enum):
    """Supported pagination strategies."""

    OFFSET = "offset"
    CURSOR = "cursor"
    KEYSET = "keyset"


class SortDirection(Enum):
    """Sort ordering direction."""

    ASC = "asc"
    DESC = "desc"


@dataclass
class PageInfo:
    """Metadata describing the current page of results."""

    has_next_page: bool = False
    has_previous_page: bool = False
    total_items: int | None = None
    total_pages: int | None = None
    current_page: int | None = None
    page_size: int = 20
    start_cursor: str | None = None
    end_cursor: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Serialize page info to a plain dictionary."""
        return {
            "has_next_page": self.has_next_page,
            "has_previous_page": self.has_previous_page,
            "total_items": self.total_items,
            "total_pages": self.total_pages,
            "current_page": self.current_page,
            "page_size": self.page_size,
            "start_cursor": self.start_cursor,
            "end_cursor": self.end_cursor,
        }

    def to_headers(self) -> dict[str, str]:
        """Convert page info to HTTP response headers."""
        headers: dict[str, str] = {
            "X-Per-Page": str(self.page_size),
            "X-Has-Next-Page": str(self.has_next_page).lower(),
            "X-Has-Previous-Page": str(self.has_previous_page).lower(),
        }

        if self.total_items is not None:
            headers["X-Total-Count"] = str(self.total_items)
        if self.current_page is not None:
            headers["X-Page"] = str(self.current_page)
        if self.total_pages is not None:
            headers["X-Total-Pages"] = str(self.total_pages)
        if self.start_cursor is not None:
            headers["X-Start-Cursor"] = self.start_cursor
        if self.end_cursor is not None:
            headers["X-End-Cursor"] = self.end_cursor

        return headers


@dataclass
class PaginatedResponse:
    """A page of results together with its metadata."""

    items: list[Any] = field(default_factory=list)
    page_info: PageInfo = field(default_factory=PageInfo)

    def to_dict(self) -> dict[str, Any]:
        """Serialize the response to a dictionary."""
        return {
            "items": self.items,
            "page_info": self.page_info.to_dict(),
        }


@dataclass
class PaginationRequest:
    """Parameters supplied by the client to control pagination."""

    page_size: int = 20
    page: int | None = None
    cursor: str | None = None
    after_key: Any | None = None
    sort_field: str | None = None
    sort_direction: SortDirection = SortDirection.ASC


class Paginator(ABC):
    """Abstract base class for pagination strategies."""

    @abstractmethod
    def paginate(
        self,
        items: list[Any],
        request: PaginationRequest,
    ) -> PaginatedResponse:
        """Paginate a list of items according to the request parameters."""
