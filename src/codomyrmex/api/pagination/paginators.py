"""Concrete paginator implementations: Offset, Cursor, Keyset, and factory."""

import base64
import math
from typing import Any

from codomyrmex.logging_monitoring import get_logger

from .models import (
    PageInfo,
    PaginatedResponse,
    PaginationRequest,
    PaginationStrategy,
    Paginator,
    SortDirection,
)

logger = get_logger(__name__)


class OffsetPaginator(Paginator):
    """Standard offset / page-number based pagination."""

    def paginate(
        self,
        items: list[Any],
        request: PaginationRequest,
    ) -> PaginatedResponse:
        """Paginate using offset / page number strategy."""
        page = request.page if request.page is not None else 1
        page_size = request.page_size
        total_items = len(items)
        total_pages = max(1, math.ceil(total_items / page_size))

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
    """Opaque cursor-based pagination using base64-encoded indices."""

    @staticmethod
    def encode_cursor(index: int) -> str:
        """Encode an integer index into an opaque base64 cursor string."""
        raw = f"cursor:{index}".encode()
        return base64.urlsafe_b64encode(raw).decode("ascii")

    @staticmethod
    def decode_cursor(cursor: str) -> int:
        """Decode an opaque cursor string back to an integer index."""
        try:
            decoded = base64.urlsafe_b64decode(cursor.encode("ascii")).decode("utf-8")
        except Exception as exc:
            raise ValueError(f"Invalid cursor: {cursor}") from exc

        if not decoded.startswith("cursor:"):
            raise ValueError(f"Invalid cursor format: {cursor}")

        try:
            return int(decoded[len("cursor:") :])
        except ValueError as exc:
            raise ValueError(f"Invalid cursor index in: {cursor}") from exc

    def paginate(
        self,
        items: list[Any],
        request: PaginationRequest,
    ) -> PaginatedResponse:
        """Paginate using cursor-based strategy."""
        total_items = len(items)
        page_size = request.page_size

        if request.cursor is not None:
            cursor_index = self.decode_cursor(request.cursor)
            start = cursor_index + 1
        else:
            start = 0

        start = max(0, min(start, total_items))
        end = min(start + page_size, total_items)
        page_items = items[start:end]

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
    """Keyset (seek) pagination based on a sort field value."""

    def __init__(self, sort_field: str = "id"):
        self._sort_field = sort_field

    def _get_field_value(self, item: Any, field_name: str) -> Any:
        """Extract the sort field value from an item."""
        if isinstance(item, dict):
            return item[field_name]
        return getattr(item, field_name)

    def _sort_items(self, items: list[Any], sort_field: str, reverse: bool) -> list[Any]:
        """Sort items by field; falls back to original order on error."""
        try:
            return sorted(
                items,
                key=lambda item: self._get_field_value(item, sort_field),
                reverse=reverse,
            )
        except (KeyError, AttributeError, TypeError):
            return list(items)

    def _find_start(self, sorted_items: list[Any], after_key: Any, sort_field: str) -> int:
        """Find the start index after the given key."""
        for i, item in enumerate(sorted_items):
            try:
                if self._get_field_value(item, sort_field) == after_key:
                    return i + 1
            except (KeyError, AttributeError):
                continue
        return 0

    def _build_cursors(
        self, page_items: list[Any], sort_field: str
    ) -> tuple[str | None, str | None]:
        """Build opaque start/end cursors from page boundary item field values."""
        try:
            first = self._get_field_value(page_items[0], sort_field)
            last = self._get_field_value(page_items[-1], sort_field)
            sc = base64.urlsafe_b64encode(f"keyset:{first}".encode()).decode("ascii")
            ec = base64.urlsafe_b64encode(f"keyset:{last}".encode()).decode("ascii")
            return sc, ec
        except (KeyError, AttributeError) as e:
            logger.debug("Failed to compute keyset cursors: %s", e)
            return None, None

    def paginate(self, items: list[Any], request: PaginationRequest) -> PaginatedResponse:
        """Paginate using keyset / seek strategy."""
        sort_field = request.sort_field or self._sort_field
        page_size = request.page_size
        reverse = request.sort_direction == SortDirection.DESC

        sorted_items = self._sort_items(items, sort_field, reverse)
        total_items = len(sorted_items)

        start = (
            self._find_start(sorted_items, request.after_key, sort_field)
            if request.after_key is not None
            else 0
        )
        end = min(start + page_size, total_items)
        page_items = sorted_items[start:end]

        start_cursor, end_cursor = self._build_cursors(page_items, sort_field) if page_items else (None, None)

        return PaginatedResponse(
            items=page_items,
            page_info=PageInfo(
                has_next_page=end < total_items,
                has_previous_page=start > 0,
                total_items=total_items,
                page_size=page_size,
                start_cursor=start_cursor,
                end_cursor=end_cursor,
            ),
        )


def create_paginator(
    strategy: PaginationStrategy = PaginationStrategy.OFFSET,
    **kwargs: Any,
) -> Paginator:
    """Create a paginator instance for the given strategy."""
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
