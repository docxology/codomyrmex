"""
Pagination Submodule

Cursor, offset, and keyset pagination utilities for API responses.
Provides strategy-based paginators with a common interface for paginating
arbitrary collections, producing standardized page metadata and HTTP headers.
"""

__version__ = "0.1.0"

import base64
import math
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

from codomyrmex.logging_monitoring.core.logger_config import get_logger

logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class PaginationStrategy(Enum):
    """Supported pagination strategies."""

    OFFSET = "offset"
    CURSOR = "cursor"
    KEYSET = "keyset"

class SortDirection(Enum):
    """Sort ordering direction."""

    ASC = "asc"
    DESC = "desc"

# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------

@dataclass
class PageInfo:
    """
    Metadata describing the current page of results.

    Carries enough information for clients to navigate through paginated
    collections regardless of the pagination strategy in use.
    """

    has_next_page: bool = False
    has_previous_page: bool = False
    total_items: int | None = None
    total_pages: int | None = None
    current_page: int | None = None
    page_size: int = 20
    start_cursor: str | None = None
    end_cursor: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Serialize page info to a plain dictionary.

        Returns:
            Dictionary containing all page metadata fields.  ``None`` values
            are included so consumers can distinguish "unknown" from "absent".
        """
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
        """Convert page info to HTTP response headers.

        Produces standard pagination headers commonly used by REST APIs:

        - ``X-Total-Count`` -- total number of items (when known).
        - ``X-Page`` -- current 1-based page number (when known).
        - ``X-Per-Page`` -- number of items per page.
        - ``X-Total-Pages`` -- total number of pages (when known).
        - ``X-Has-Next-Page`` -- ``"true"`` / ``"false"``.
        - ``X-Has-Previous-Page`` -- ``"true"`` / ``"false"``.
        - ``X-Start-Cursor`` -- opaque cursor for the first item on the page.
        - ``X-End-Cursor`` -- opaque cursor for the last item on the page.

        Returns:
            Dictionary of header name to header value strings.
        """
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
    """
    A page of results together with its metadata.

    This is the standard return type produced by all :class:`Paginator`
    implementations.
    """

    items: list[Any] = field(default_factory=list)
    page_info: PageInfo = field(default_factory=PageInfo)

    def to_dict(self) -> dict[str, Any]:
        """Serialize the response to a dictionary.

        Returns:
            ``{"items": [...], "page_info": {...}}``
        """
        return {
            "items": self.items,
            "page_info": self.page_info.to_dict(),
        }

@dataclass
class PaginationRequest:
    """
    Parameters supplied by the client to control pagination.

    Different pagination strategies use different subsets of these fields:

    - **Offset**: ``page`` and ``page_size``.
    - **Cursor**: ``cursor`` and ``page_size``.
    - **Keyset**: ``after_key``, ``sort_field``, ``sort_direction``, and
      ``page_size``.
    """

    page_size: int = 20
    page: int | None = None
    cursor: str | None = None
    after_key: Any | None = None
    sort_field: str | None = None
    sort_direction: SortDirection = SortDirection.ASC

# ---------------------------------------------------------------------------
# Abstract base class
# ---------------------------------------------------------------------------

class Paginator(ABC):
    """Abstract base class for pagination strategies.

    Concrete subclasses implement a single ``paginate`` method that accepts an
    in-memory list of items together with a :class:`PaginationRequest` and
    returns a :class:`PaginatedResponse`.
    """

    @abstractmethod
    def paginate(
        self,
        items: list[Any],
        request: PaginationRequest,
    ) -> PaginatedResponse:
        """Paginate a list of items according to the request parameters.

        Args:
            items: The full collection of items to paginate.
            request: Client-supplied pagination parameters.

        Returns:
            A :class:`PaginatedResponse` containing the requested page and
            metadata.
        """
        pass

# ---------------------------------------------------------------------------
# Concrete implementations
# ---------------------------------------------------------------------------

class OffsetPaginator(Paginator):
    """Standard offset / page-number based pagination.

    Slices the item list using a 1-based ``page`` number and ``page_size``.
    If no ``page`` is provided in the request it defaults to ``1``.

    Example::

        paginator = OffsetPaginator()
        request = PaginationRequest(page=2, page_size=10)
        response = paginator.paginate(all_items, request)
    """

    def paginate(
        self,
        items: list[Any],
        request: PaginationRequest,
    ) -> PaginatedResponse:
        """Paginate using offset / page number strategy.

        Args:
            items: The full collection of items.
            request: Must include ``page`` (defaults to 1) and ``page_size``.

        Returns:
            A :class:`PaginatedResponse` with fully-populated
            :class:`PageInfo` including ``total_items``, ``total_pages``,
            ``current_page``, ``has_next_page``, and ``has_previous_page``.
        """
        page = request.page if request.page is not None else 1
        page_size = request.page_size
        total_items = len(items)
        total_pages = max(1, math.ceil(total_items / page_size))

        # Clamp page to valid range
        page = max(1, min(page, total_pages))

        start = (page - 1) * page_size
        end = start + page_size
        page_items = items[start:end]

        page_info = PageInfo(
            has_next_page=end < total_items,
            has_previous_page=page > 1,
            total_items=total_items,
            total_pages=total_pages,
            current_page=page,
            page_size=page_size,
        )

        return PaginatedResponse(items=page_items, page_info=page_info)

class CursorPaginator(Paginator):
    """Opaque cursor-based pagination using base64-encoded indices.

    Cursors encode the item index as a base64 string, making them opaque
    to clients while remaining simple to decode on the server.

    Example::

        paginator = CursorPaginator()
        # First page (no cursor)
        request = PaginationRequest(page_size=10)
        response = paginator.paginate(all_items, request)
        # Next page
        next_req = PaginationRequest(
            page_size=10,
            cursor=response.page_info.end_cursor,
        )
        next_response = paginator.paginate(all_items, next_req)
    """

    @staticmethod
    def encode_cursor(index: int) -> str:
        """Encode an integer index into an opaque base64 cursor string.

        Args:
            index: The 0-based index to encode.

        Returns:
            A URL-safe base64 encoded string representing the index.
        """
        raw = f"cursor:{index}".encode()
        return base64.urlsafe_b64encode(raw).decode("ascii")

    @staticmethod
    def decode_cursor(cursor: str) -> int:
        """Decode an opaque cursor string back to an integer index.

        Args:
            cursor: A cursor string previously produced by
                :meth:`encode_cursor`.

        Returns:
            The 0-based index encoded in the cursor.

        Raises:
            ValueError: If the cursor cannot be decoded or has an invalid
                format.
        """
        try:
            decoded = base64.urlsafe_b64decode(cursor.encode("ascii")).decode("utf-8")
        except Exception as exc:
            raise ValueError(f"Invalid cursor: {cursor}") from exc

        if not decoded.startswith("cursor:"):
            raise ValueError(f"Invalid cursor format: {cursor}")

        try:
            return int(decoded[len("cursor:"):])
        except ValueError as exc:
            raise ValueError(f"Invalid cursor index in: {cursor}") from exc

    def paginate(
        self,
        items: list[Any],
        request: PaginationRequest,
    ) -> PaginatedResponse:
        """Paginate using cursor-based strategy.

        Args:
            items: The full collection of items.
            request: If ``cursor`` is provided the page starts *after* the
                position encoded in the cursor.  Otherwise the first page is
                returned.

        Returns:
            A :class:`PaginatedResponse` with ``start_cursor`` and
            ``end_cursor`` set on the :class:`PageInfo`.
        """
        total_items = len(items)
        page_size = request.page_size

        # Determine start position
        if request.cursor is not None:
            cursor_index = self.decode_cursor(request.cursor)
            start = cursor_index + 1  # Start after the cursor position
        else:
            start = 0

        # Clamp start
        start = max(0, min(start, total_items))

        end = min(start + page_size, total_items)
        page_items = items[start:end]

        # Build cursors
        start_cursor: str | None = None
        end_cursor: str | None = None
        if page_items:
            start_cursor = self.encode_cursor(start)
            end_cursor = self.encode_cursor(end - 1)

        page_info = PageInfo(
            has_next_page=end < total_items,
            has_previous_page=start > 0,
            total_items=total_items,
            page_size=page_size,
            start_cursor=start_cursor,
            end_cursor=end_cursor,
        )

        return PaginatedResponse(items=page_items, page_info=page_info)

class KeysetPaginator(Paginator):
    """Keyset (seek) pagination based on a sort field value.

    Items are sorted by the specified ``sort_field`` and the page starts
    after the item whose sort field value matches ``after_key``.

    This strategy is efficient for large datasets because it avoids
    counting offsets from the beginning of the collection.

    Args:
        sort_field: The attribute or dictionary key to sort and seek on.
            Can be overridden per-request via
            :attr:`PaginationRequest.sort_field`.

    Example::

        paginator = KeysetPaginator(sort_field="id")
        request = PaginationRequest(page_size=10, after_key=42)
        response = paginator.paginate(all_items, request)
    """

    def __init__(self, sort_field: str = "id"):
        self._sort_field = sort_field

    def _get_field_value(self, item: Any, field_name: str) -> Any:
        """Extract the sort field value from an item.

        Supports both dictionary-style and attribute-style access.

        Args:
            item: The item to extract the field from.
            field_name: The field/key name.

        Returns:
            The value of the field on the item.

        Raises:
            KeyError: If the item is a dict and the key is missing.
            AttributeError: If the item is an object and lacks the attribute.
        """
        if isinstance(item, dict):
            return item[field_name]
        return getattr(item, field_name)

    def paginate(
        self,
        items: list[Any],
        request: PaginationRequest,
    ) -> PaginatedResponse:
        """Paginate using keyset / seek strategy.

        Args:
            items: The full collection of items. The method will sort these
                internally by the sort field.
            request: ``after_key`` determines where the page starts.
                ``sort_field`` on the request overrides the paginator's
                default.  ``sort_direction`` controls ordering.

        Returns:
            A :class:`PaginatedResponse` with cursor information derived
            from the sort field values.
        """
        sort_field = request.sort_field or self._sort_field
        page_size = request.page_size
        reverse = request.sort_direction == SortDirection.DESC

        # Sort items by the keyset field
        try:
            sorted_items = sorted(
                items,
                key=lambda item: self._get_field_value(item, sort_field),
                reverse=reverse,
            )
        except (KeyError, AttributeError, TypeError):
            # If sorting fails, fall back to original order
            sorted_items = list(items)

        total_items = len(sorted_items)

        # Find the start position based on after_key
        if request.after_key is not None:
            start = 0
            for i, item in enumerate(sorted_items):
                try:
                    value = self._get_field_value(item, sort_field)
                    if value == request.after_key:
                        start = i + 1
                        break
                except (KeyError, AttributeError):
                    continue
            else:
                # after_key not found -- start from the beginning
                start = 0
        else:
            start = 0

        end = min(start + page_size, total_items)
        page_items = sorted_items[start:end]

        # Build cursors from the sort field values of boundary items
        start_cursor: str | None = None
        end_cursor: str | None = None
        if page_items:
            try:
                first_value = self._get_field_value(page_items[0], sort_field)
                last_value = self._get_field_value(page_items[-1], sort_field)
                start_cursor = base64.urlsafe_b64encode(
                    f"keyset:{first_value}".encode()
                ).decode("ascii")
                end_cursor = base64.urlsafe_b64encode(
                    f"keyset:{last_value}".encode()
                ).decode("ascii")
            except (KeyError, AttributeError) as e:
                logger.debug("Failed to compute keyset cursors for pagination: %s", e)

        page_info = PageInfo(
            has_next_page=end < total_items,
            has_previous_page=start > 0,
            total_items=total_items,
            page_size=page_size,
            start_cursor=start_cursor,
            end_cursor=end_cursor,
        )

        return PaginatedResponse(items=page_items, page_info=page_info)

# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------

def create_paginator(
    strategy: PaginationStrategy = PaginationStrategy.OFFSET,
    **kwargs: Any,
) -> Paginator:
    """Create a paginator instance for the given strategy.

    This is the recommended way to obtain a :class:`Paginator`.  It maps
    a :class:`PaginationStrategy` enum value to the corresponding concrete
    class, forwarding any extra keyword arguments to the constructor.

    Args:
        strategy: The pagination strategy to use.
        **kwargs: Additional keyword arguments passed to the paginator
            constructor (e.g. ``sort_field`` for :class:`KeysetPaginator`).

    Returns:
        A :class:`Paginator` instance configured for the requested strategy.

    Raises:
        ValueError: If an unknown strategy is provided.

    Example::

        paginator = create_paginator(PaginationStrategy.CURSOR)
        response = paginator.paginate(items, PaginationRequest(page_size=25))
    """
    _strategy_map: dict[PaginationStrategy, type] = {
        PaginationStrategy.OFFSET: OffsetPaginator,
        PaginationStrategy.CURSOR: CursorPaginator,
        PaginationStrategy.KEYSET: KeysetPaginator,
    }

    paginator_class = _strategy_map.get(strategy)
    if paginator_class is None:
        raise ValueError(
            f"Unknown pagination strategy: {strategy!r}. "
            f"Valid strategies: {', '.join(s.value for s in PaginationStrategy)}"
        )

    return paginator_class(**kwargs)

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

__all__ = [
    # Enums
    "PaginationStrategy",
    "SortDirection",
    # Dataclasses
    "PageInfo",
    "PaginatedResponse",
    "PaginationRequest",
    # Abstract base
    "Paginator",
    # Concrete paginators
    "OffsetPaginator",
    "CursorPaginator",
    "KeysetPaginator",
    # Factory
    "create_paginator",
]
