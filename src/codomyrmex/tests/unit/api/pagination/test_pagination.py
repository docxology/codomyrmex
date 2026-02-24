"""Comprehensive tests for the codomyrmex.api.pagination module.

Tests cover all public API surface: dataclasses, enums, concrete paginators,
cursor encoding/decoding, and the factory function.
"""

import pytest

from codomyrmex.api.pagination import (
    CursorPaginator,
    KeysetPaginator,
    OffsetPaginator,
    PageInfo,
    PaginatedResponse,
    PaginationRequest,
    PaginationStrategy,
    SortDirection,
    create_paginator,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_items():
    """A simple list of 25 integers for pagination tests."""
    return list(range(1, 26))


@pytest.fixture
def dict_items():
    """A list of dictionaries with an 'id' key, useful for keyset tests."""
    return [{"id": i, "name": f"item-{i}"} for i in range(1, 16)]


# ---------------------------------------------------------------------------
# PageInfo
# ---------------------------------------------------------------------------

class TestPageInfo:
    """Tests for the PageInfo dataclass."""

    def test_to_dict_with_defaults(self):
        """Test functionality: to dict with defaults."""
        info = PageInfo()
        d = info.to_dict()
        assert d["has_next_page"] is False
        assert d["has_previous_page"] is False
        assert d["total_items"] is None
        assert d["total_pages"] is None
        assert d["current_page"] is None
        assert d["page_size"] == 20
        assert d["start_cursor"] is None
        assert d["end_cursor"] is None

    def test_to_dict_with_populated_fields(self):
        """Test functionality: to dict with populated fields."""
        info = PageInfo(
            has_next_page=True,
            has_previous_page=True,
            total_items=100,
            total_pages=10,
            current_page=3,
            page_size=10,
            start_cursor="sc",
            end_cursor="ec",
        )
        d = info.to_dict()
        assert d["has_next_page"] is True
        assert d["total_items"] == 100
        assert d["current_page"] == 3
        assert d["start_cursor"] == "sc"

    def test_to_headers_minimal(self):
        """Test functionality: to headers minimal."""
        info = PageInfo()
        headers = info.to_headers()
        assert headers["X-Per-Page"] == "20"
        assert headers["X-Has-Next-Page"] == "false"
        assert headers["X-Has-Previous-Page"] == "false"
        assert "X-Total-Count" not in headers
        assert "X-Page" not in headers

    def test_to_headers_full(self):
        """Test functionality: to headers full."""
        info = PageInfo(
            has_next_page=True,
            has_previous_page=False,
            total_items=50,
            total_pages=5,
            current_page=2,
            page_size=10,
            start_cursor="abc",
            end_cursor="xyz",
        )
        headers = info.to_headers()
        assert headers["X-Total-Count"] == "50"
        assert headers["X-Page"] == "2"
        assert headers["X-Per-Page"] == "10"
        assert headers["X-Total-Pages"] == "5"
        assert headers["X-Has-Next-Page"] == "true"
        assert headers["X-Has-Previous-Page"] == "false"
        assert headers["X-Start-Cursor"] == "abc"
        assert headers["X-End-Cursor"] == "xyz"


# ---------------------------------------------------------------------------
# PaginatedResponse
# ---------------------------------------------------------------------------

class TestPaginatedResponse:
    """Tests for the PaginatedResponse dataclass."""

    def test_to_dict_defaults(self):
        """Test functionality: to dict defaults."""
        resp = PaginatedResponse()
        d = resp.to_dict()
        assert d["items"] == []
        assert d["page_info"]["page_size"] == 20

    def test_to_dict_with_items(self):
        """Test functionality: to dict with items."""
        items = [1, 2, 3]
        info = PageInfo(has_next_page=True, total_items=10, page_size=3)
        resp = PaginatedResponse(items=items, page_info=info)
        d = resp.to_dict()
        assert d["items"] == [1, 2, 3]
        assert d["page_info"]["has_next_page"] is True
        assert d["page_info"]["total_items"] == 10


# ---------------------------------------------------------------------------
# PaginationRequest
# ---------------------------------------------------------------------------

class TestPaginationRequest:
    """Tests for the PaginationRequest dataclass defaults."""

    def test_defaults(self):
        """Test functionality: defaults."""
        req = PaginationRequest()
        assert req.page_size == 20
        assert req.page is None
        assert req.cursor is None
        assert req.after_key is None
        assert req.sort_field is None
        assert req.sort_direction == SortDirection.ASC


# ---------------------------------------------------------------------------
# OffsetPaginator
# ---------------------------------------------------------------------------

class TestOffsetPaginator:
    """Tests for OffsetPaginator (page-number based, 1-indexed)."""

    def test_first_page(self, sample_items):
        """Test functionality: first page."""
        paginator = OffsetPaginator()
        req = PaginationRequest(page=1, page_size=10)
        resp = paginator.paginate(sample_items, req)
        assert resp.items == list(range(1, 11))
        assert resp.page_info.current_page == 1
        assert resp.page_info.has_next_page is True
        assert resp.page_info.has_previous_page is False
        assert resp.page_info.total_items == 25
        assert resp.page_info.total_pages == 3

    def test_middle_page(self, sample_items):
        """Test functionality: middle page."""
        paginator = OffsetPaginator()
        req = PaginationRequest(page=2, page_size=10)
        resp = paginator.paginate(sample_items, req)
        assert resp.items == list(range(11, 21))
        assert resp.page_info.current_page == 2
        assert resp.page_info.has_next_page is True
        assert resp.page_info.has_previous_page is True

    def test_last_page(self, sample_items):
        """Test functionality: last page."""
        paginator = OffsetPaginator()
        req = PaginationRequest(page=3, page_size=10)
        resp = paginator.paginate(sample_items, req)
        assert resp.items == list(range(21, 26))
        assert resp.page_info.current_page == 3
        assert resp.page_info.has_next_page is False
        assert resp.page_info.has_previous_page is True

    def test_beyond_last_page_clamped(self, sample_items):
        """Test functionality: beyond last page clamped."""
        paginator = OffsetPaginator()
        req = PaginationRequest(page=999, page_size=10)
        resp = paginator.paginate(sample_items, req)
        # Page should be clamped to the last valid page (3)
        assert resp.page_info.current_page == 3
        assert resp.items == list(range(21, 26))
        assert resp.page_info.has_next_page is False

    def test_default_page_is_one(self, sample_items):
        """Test functionality: default page is one."""
        paginator = OffsetPaginator()
        req = PaginationRequest(page_size=5)
        resp = paginator.paginate(sample_items, req)
        assert resp.page_info.current_page == 1
        assert resp.items == list(range(1, 6))

    def test_has_next_and_previous_boundaries(self):
        """Test functionality: has next and previous boundaries."""
        items = list(range(10))
        paginator = OffsetPaginator()

        # Single page -- neither next nor previous
        resp = paginator.paginate(items, PaginationRequest(page=1, page_size=10))
        assert resp.page_info.has_next_page is False
        assert resp.page_info.has_previous_page is False

        # Two pages -- first has next, second has previous
        resp1 = paginator.paginate(items, PaginationRequest(page=1, page_size=5))
        assert resp1.page_info.has_next_page is True
        assert resp1.page_info.has_previous_page is False

        resp2 = paginator.paginate(items, PaginationRequest(page=2, page_size=5))
        assert resp2.page_info.has_next_page is False
        assert resp2.page_info.has_previous_page is True


# ---------------------------------------------------------------------------
# CursorPaginator
# ---------------------------------------------------------------------------

class TestCursorPaginator:
    """Tests for CursorPaginator (base64 opaque cursors)."""

    def test_encode_decode_roundtrip(self):
        """Test functionality: encode decode roundtrip."""
        for index in (0, 1, 42, 9999):
            cursor = CursorPaginator.encode_cursor(index)
            assert isinstance(cursor, str)
            assert CursorPaginator.decode_cursor(cursor) == index

    def test_decode_invalid_cursor_raises(self):
        """Test functionality: decode invalid cursor raises."""
        with pytest.raises(ValueError, match="Invalid cursor"):
            CursorPaginator.decode_cursor("not-a-valid-cursor!!!")

    def test_decode_wrong_format_raises(self):
        """Test functionality: decode wrong format raises."""
        import base64
        bad = base64.urlsafe_b64encode(b"wrong:42").decode("ascii")
        with pytest.raises(ValueError, match="Invalid cursor format"):
            CursorPaginator.decode_cursor(bad)

    def test_first_page_no_cursor(self, sample_items):
        """Test functionality: first page no cursor."""
        paginator = CursorPaginator()
        req = PaginationRequest(page_size=10)
        resp = paginator.paginate(sample_items, req)
        assert resp.items == list(range(1, 11))
        assert resp.page_info.has_next_page is True
        assert resp.page_info.has_previous_page is False
        assert resp.page_info.start_cursor is not None
        assert resp.page_info.end_cursor is not None
        assert resp.page_info.total_items == 25

    def test_next_page_using_end_cursor(self, sample_items):
        """Test functionality: next page using end cursor."""
        paginator = CursorPaginator()
        first_req = PaginationRequest(page_size=10)
        first_resp = paginator.paginate(sample_items, first_req)

        second_req = PaginationRequest(
            page_size=10,
            cursor=first_resp.page_info.end_cursor,
        )
        second_resp = paginator.paginate(sample_items, second_req)
        assert second_resp.items == list(range(11, 21))
        assert second_resp.page_info.has_previous_page is True
        assert second_resp.page_info.has_next_page is True

    def test_cursor_pagination_exhausts_items(self, sample_items):
        """Test functionality: cursor pagination exhausts items."""
        paginator = CursorPaginator()
        all_collected = []
        cursor = None

        while True:
            req = PaginationRequest(page_size=10, cursor=cursor)
            resp = paginator.paginate(sample_items, req)
            all_collected.extend(resp.items)
            if not resp.page_info.has_next_page:
                break
            cursor = resp.page_info.end_cursor

        assert all_collected == sample_items

    def test_has_previous_page_on_second_page(self, sample_items):
        """Test functionality: has previous page on second page."""
        paginator = CursorPaginator()
        first = paginator.paginate(sample_items, PaginationRequest(page_size=10))
        second = paginator.paginate(
            sample_items,
            PaginationRequest(page_size=10, cursor=first.page_info.end_cursor),
        )
        assert second.page_info.has_previous_page is True


# ---------------------------------------------------------------------------
# KeysetPaginator
# ---------------------------------------------------------------------------

class TestKeysetPaginator:
    """Tests for KeysetPaginator using dict items and sort_field='id'."""

    def test_first_page_default_sort(self, dict_items):
        """Test functionality: first page default sort."""
        paginator = KeysetPaginator(sort_field="id")
        req = PaginationRequest(page_size=5)
        resp = paginator.paginate(dict_items, req)
        assert [it["id"] for it in resp.items] == [1, 2, 3, 4, 5]
        assert resp.page_info.has_next_page is True
        assert resp.page_info.has_previous_page is False

    def test_after_key_pagination(self, dict_items):
        """Test functionality: after key pagination."""
        paginator = KeysetPaginator(sort_field="id")
        req = PaginationRequest(page_size=5, after_key=5)
        resp = paginator.paginate(dict_items, req)
        assert [it["id"] for it in resp.items] == [6, 7, 8, 9, 10]
        assert resp.page_info.has_previous_page is True
        assert resp.page_info.has_next_page is True

    def test_desc_sort_direction(self, dict_items):
        """Test functionality: desc sort direction."""
        paginator = KeysetPaginator(sort_field="id")
        req = PaginationRequest(
            page_size=5,
            sort_direction=SortDirection.DESC,
        )
        resp = paginator.paginate(dict_items, req)
        assert [it["id"] for it in resp.items] == [15, 14, 13, 12, 11]
        assert resp.page_info.has_next_page is True

    def test_missing_key_handled_gracefully(self):
        """Test functionality: missing key handled gracefully."""
        items = [{"x": 1}, {"x": 2}, {"x": 3}]
        paginator = KeysetPaginator(sort_field="nonexistent")
        req = PaginationRequest(page_size=2)
        # Should not raise; falls back to original order
        resp = paginator.paginate(items, req)
        assert len(resp.items) == 2

    def test_keyset_cursors_are_set(self, dict_items):
        """Test functionality: keyset cursors are set."""
        paginator = KeysetPaginator(sort_field="id")
        req = PaginationRequest(page_size=5)
        resp = paginator.paginate(dict_items, req)
        assert resp.page_info.start_cursor is not None
        assert resp.page_info.end_cursor is not None

    def test_after_key_not_found_starts_from_beginning(self, dict_items):
        """Test functionality: after key not found starts from beginning."""
        paginator = KeysetPaginator(sort_field="id")
        req = PaginationRequest(page_size=5, after_key=9999)
        resp = paginator.paginate(dict_items, req)
        # When after_key is not found, pagination starts from the beginning
        assert [it["id"] for it in resp.items] == [1, 2, 3, 4, 5]


# ---------------------------------------------------------------------------
# create_paginator factory
# ---------------------------------------------------------------------------

class TestCreatePaginator:
    """Tests for the create_paginator factory function."""

    def test_offset_strategy(self):
        """Test functionality: offset strategy."""
        p = create_paginator(PaginationStrategy.OFFSET)
        assert isinstance(p, OffsetPaginator)

    def test_cursor_strategy(self):
        """Test functionality: cursor strategy."""
        p = create_paginator(PaginationStrategy.CURSOR)
        assert isinstance(p, CursorPaginator)

    def test_keyset_strategy(self):
        """Test functionality: keyset strategy."""
        p = create_paginator(PaginationStrategy.KEYSET)
        assert isinstance(p, KeysetPaginator)

    def test_keyset_with_sort_field_kwarg(self):
        """Test functionality: keyset with sort field kwarg."""
        p = create_paginator(PaginationStrategy.KEYSET, sort_field="name")
        assert isinstance(p, KeysetPaginator)
        assert p._sort_field == "name"

    def test_unknown_strategy_raises(self):
        """Test functionality: unknown strategy raises."""
        with pytest.raises(ValueError, match="Unknown pagination strategy"):
            create_paginator("not_a_strategy")
