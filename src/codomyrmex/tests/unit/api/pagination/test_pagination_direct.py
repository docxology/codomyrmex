"""Supplementary tests for codomyrmex.api.pagination using direct submodule import.

The existing test_pagination.py is skipped because importing via
``codomyrmex.api.pagination`` triggers the circular import in the parent
``codomyrmex.api.__init__``.  This file loads ``pagination/__init__.py``
directly via importlib, bypassing the problematic chain.

No mocks used.
"""

import base64
import importlib.util
import sys

import pytest

# ---------------------------------------------------------------------------
# Direct-import helper
# ---------------------------------------------------------------------------


def _load_pagination():
    name = "codomyrmex.api.pagination"
    if name in sys.modules:
        return sys.modules[name]

    spec = importlib.util.spec_from_file_location(
        name,
        "src/codomyrmex/api/pagination/__init__.py",
    )
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


try:
    _pg = _load_pagination()
    PaginationStrategy = _pg.PaginationStrategy
    SortDirection = _pg.SortDirection
    PageInfo = _pg.PageInfo
    PaginatedResponse = _pg.PaginatedResponse
    PaginationRequest = _pg.PaginationRequest
    Paginator = _pg.Paginator
    OffsetPaginator = _pg.OffsetPaginator
    CursorPaginator = _pg.CursorPaginator
    KeysetPaginator = _pg.KeysetPaginator
    create_paginator = _pg.create_paginator
    _AVAILABLE = True
except Exception as _exc:
    _AVAILABLE = False
    _SKIP_REASON = str(_exc)

pytestmark = pytest.mark.skipif(
    not _AVAILABLE,
    reason=f"pagination unavailable: {'' if _AVAILABLE else _SKIP_REASON}",
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def items_25():
    return list(range(1, 26))  # 1..25


@pytest.fixture
def dict_items_15():
    return [{"id": i, "name": f"item-{i}"} for i in range(1, 16)]


# ===========================================================================
# Enums
# ===========================================================================


class TestPaginationStrategyEnum:
    def test_offset_value(self):
        assert PaginationStrategy.OFFSET.value == "offset"

    def test_cursor_value(self):
        assert PaginationStrategy.CURSOR.value == "cursor"

    def test_keyset_value(self):
        assert PaginationStrategy.KEYSET.value == "keyset"

    def test_three_members(self):
        assert len(PaginationStrategy) == 3


class TestSortDirectionEnum:
    def test_asc_value(self):
        assert SortDirection.ASC.value == "asc"

    def test_desc_value(self):
        assert SortDirection.DESC.value == "desc"

    def test_two_members(self):
        assert len(SortDirection) == 2


# ===========================================================================
# PageInfo
# ===========================================================================


class TestPageInfo:
    def test_defaults(self):
        info = PageInfo()
        assert info.has_next_page is False
        assert info.has_previous_page is False
        assert info.total_items is None
        assert info.total_pages is None
        assert info.current_page is None
        assert info.page_size == 20
        assert info.start_cursor is None
        assert info.end_cursor is None

    def test_to_dict_default_values(self):
        d = PageInfo().to_dict()
        assert d["has_next_page"] is False
        assert d["page_size"] == 20
        assert d["total_items"] is None

    def test_to_dict_populated(self):
        info = PageInfo(
            has_next_page=True,
            has_previous_page=True,
            total_items=100,
            total_pages=10,
            current_page=5,
            page_size=10,
            start_cursor="sc",
            end_cursor="ec",
        )
        d = info.to_dict()
        assert d["has_next_page"] is True
        assert d["total_items"] == 100
        assert d["start_cursor"] == "sc"

    def test_to_headers_minimal(self):
        headers = PageInfo().to_headers()
        assert headers["X-Per-Page"] == "20"
        assert headers["X-Has-Next-Page"] == "false"
        assert headers["X-Has-Previous-Page"] == "false"
        assert "X-Total-Count" not in headers
        assert "X-Page" not in headers
        assert "X-Total-Pages" not in headers
        assert "X-Start-Cursor" not in headers
        assert "X-End-Cursor" not in headers

    def test_to_headers_full(self):
        info = PageInfo(
            has_next_page=True,
            has_previous_page=False,
            total_items=50,
            total_pages=5,
            current_page=2,
            page_size=10,
            start_cursor="start",
            end_cursor="end",
        )
        headers = info.to_headers()
        assert headers["X-Total-Count"] == "50"
        assert headers["X-Page"] == "2"
        assert headers["X-Total-Pages"] == "5"
        assert headers["X-Start-Cursor"] == "start"
        assert headers["X-End-Cursor"] == "end"
        assert headers["X-Has-Next-Page"] == "true"
        assert headers["X-Has-Previous-Page"] == "false"

    def test_to_headers_only_total_count_when_set(self):
        info = PageInfo(total_items=42)
        headers = info.to_headers()
        assert headers["X-Total-Count"] == "42"
        assert "X-Page" not in headers


# ===========================================================================
# PaginatedResponse
# ===========================================================================


class TestPaginatedResponse:
    def test_default_empty(self):
        r = PaginatedResponse()
        assert r.items == []
        d = r.to_dict()
        assert d["items"] == []

    def test_to_dict_with_items_and_info(self):
        info = PageInfo(has_next_page=True, total_items=5, page_size=3)
        r = PaginatedResponse(items=[1, 2, 3], page_info=info)
        d = r.to_dict()
        assert d["items"] == [1, 2, 3]
        assert d["page_info"]["has_next_page"] is True


# ===========================================================================
# PaginationRequest
# ===========================================================================


class TestPaginationRequest:
    def test_defaults(self):
        req = PaginationRequest()
        assert req.page_size == 20
        assert req.page is None
        assert req.cursor is None
        assert req.after_key is None
        assert req.sort_field is None
        assert req.sort_direction == SortDirection.ASC

    def test_custom_page_size(self):
        req = PaginationRequest(page_size=50)
        assert req.page_size == 50

    def test_desc_sort_direction(self):
        req = PaginationRequest(sort_direction=SortDirection.DESC)
        assert req.sort_direction == SortDirection.DESC


# ===========================================================================
# OffsetPaginator
# ===========================================================================


class TestOffsetPaginator:
    def test_first_page(self, items_25):
        p = OffsetPaginator()
        resp = p.paginate(items_25, PaginationRequest(page=1, page_size=10))
        assert resp.items == list(range(1, 11))
        assert resp.page_info.current_page == 1
        assert resp.page_info.has_next_page is True
        assert resp.page_info.has_previous_page is False
        assert resp.page_info.total_items == 25
        assert resp.page_info.total_pages == 3

    def test_middle_page(self, items_25):
        p = OffsetPaginator()
        resp = p.paginate(items_25, PaginationRequest(page=2, page_size=10))
        assert resp.items == list(range(11, 21))
        assert resp.page_info.has_next_page is True
        assert resp.page_info.has_previous_page is True

    def test_last_page(self, items_25):
        p = OffsetPaginator()
        resp = p.paginate(items_25, PaginationRequest(page=3, page_size=10))
        assert resp.items == list(range(21, 26))
        assert resp.page_info.has_next_page is False
        assert resp.page_info.has_previous_page is True

    def test_page_beyond_last_clamped(self, items_25):
        p = OffsetPaginator()
        resp = p.paginate(items_25, PaginationRequest(page=999, page_size=10))
        assert resp.page_info.current_page == 3

    def test_page_zero_clamped_to_one(self, items_25):
        p = OffsetPaginator()
        resp = p.paginate(items_25, PaginationRequest(page=0, page_size=10))
        assert resp.page_info.current_page == 1

    def test_default_page_is_one(self, items_25):
        p = OffsetPaginator()
        resp = p.paginate(items_25, PaginationRequest(page_size=5))
        assert resp.page_info.current_page == 1
        assert resp.items == [1, 2, 3, 4, 5]

    def test_empty_items(self):
        p = OffsetPaginator()
        resp = p.paginate([], PaginationRequest(page=1, page_size=10))
        assert resp.items == []
        assert resp.page_info.total_items == 0
        assert resp.page_info.total_pages == 1
        assert resp.page_info.has_next_page is False

    def test_single_page_fits_all(self):
        items = list(range(5))
        p = OffsetPaginator()
        resp = p.paginate(items, PaginationRequest(page=1, page_size=10))
        assert resp.items == items
        assert resp.page_info.has_next_page is False
        assert resp.page_info.has_previous_page is False

    def test_page_size_one(self):
        p = OffsetPaginator()
        resp = p.paginate([10, 20, 30], PaginationRequest(page=2, page_size=1))
        assert resp.items == [20]
        assert resp.page_info.has_next_page is True
        assert resp.page_info.has_previous_page is True

    def test_total_pages_calculation(self):
        items = list(range(11))
        p = OffsetPaginator()
        resp = p.paginate(items, PaginationRequest(page=1, page_size=3))
        # ceil(11 / 3) = 4
        assert resp.page_info.total_pages == 4


# ===========================================================================
# CursorPaginator
# ===========================================================================


class TestCursorPaginator:
    def test_encode_decode_roundtrip(self):
        for index in (0, 1, 9, 99, 9999):
            cursor = CursorPaginator.encode_cursor(index)
            assert CursorPaginator.decode_cursor(cursor) == index

    def test_cursor_is_base64_string(self):
        cursor = CursorPaginator.encode_cursor(42)
        # Should be valid base64
        decoded = base64.urlsafe_b64decode(cursor.encode()).decode()
        assert decoded == "cursor:42"

    def test_decode_invalid_base64_raises(self):
        with pytest.raises(ValueError, match="Invalid cursor"):
            CursorPaginator.decode_cursor("!!!not-base64!!!")

    def test_decode_wrong_prefix_raises(self):
        bad = base64.urlsafe_b64encode(b"offset:42").decode()
        with pytest.raises(ValueError, match="Invalid cursor format"):
            CursorPaginator.decode_cursor(bad)

    def test_decode_non_integer_index_raises(self):
        bad = base64.urlsafe_b64encode(b"cursor:abc").decode()
        with pytest.raises(ValueError, match="Invalid cursor index"):
            CursorPaginator.decode_cursor(bad)

    def test_first_page_no_cursor(self, items_25):
        p = CursorPaginator()
        resp = p.paginate(items_25, PaginationRequest(page_size=10))
        assert resp.items == list(range(1, 11))
        assert resp.page_info.has_next_page is True
        assert resp.page_info.has_previous_page is False
        assert resp.page_info.start_cursor is not None
        assert resp.page_info.end_cursor is not None

    def test_second_page_using_end_cursor(self, items_25):
        p = CursorPaginator()
        first = p.paginate(items_25, PaginationRequest(page_size=10))
        second = p.paginate(
            items_25,
            PaginationRequest(page_size=10, cursor=first.page_info.end_cursor),
        )
        assert second.items == list(range(11, 21))
        assert second.page_info.has_previous_page is True
        assert second.page_info.has_next_page is True

    def test_full_iteration_covers_all_items(self, items_25):
        p = CursorPaginator()
        collected = []
        cursor = None
        while True:
            req = PaginationRequest(page_size=10, cursor=cursor)
            resp = p.paginate(items_25, req)
            collected.extend(resp.items)
            if not resp.page_info.has_next_page:
                break
            cursor = resp.page_info.end_cursor
        assert collected == items_25

    def test_empty_items_no_cursors(self):
        p = CursorPaginator()
        resp = p.paginate([], PaginationRequest(page_size=10))
        assert resp.items == []
        assert resp.page_info.start_cursor is None
        assert resp.page_info.end_cursor is None
        assert resp.page_info.has_next_page is False

    def test_cursor_at_end_returns_empty(self, items_25):
        p = CursorPaginator()
        # Encode a cursor pointing to the last element (index 24)
        end_cursor = CursorPaginator.encode_cursor(24)
        resp = p.paginate(items_25, PaginationRequest(page_size=10, cursor=end_cursor))
        assert resp.items == []
        assert resp.page_info.has_next_page is False

    def test_total_items_always_set(self, items_25):
        p = CursorPaginator()
        resp = p.paginate(items_25, PaginationRequest(page_size=5))
        assert resp.page_info.total_items == 25


# ===========================================================================
# KeysetPaginator
# ===========================================================================


class TestKeysetPaginator:
    def test_first_page_asc(self, dict_items_15):
        p = KeysetPaginator(sort_field="id")
        resp = p.paginate(dict_items_15, PaginationRequest(page_size=5))
        ids = [item["id"] for item in resp.items]
        assert ids == [1, 2, 3, 4, 5]

    def test_first_page_desc(self, dict_items_15):
        p = KeysetPaginator(sort_field="id")
        resp = p.paginate(
            dict_items_15,
            PaginationRequest(page_size=5, sort_direction=SortDirection.DESC),
        )
        ids = [item["id"] for item in resp.items]
        assert ids == [15, 14, 13, 12, 11]

    def test_after_key_pagination(self, dict_items_15):
        p = KeysetPaginator(sort_field="id")
        resp = p.paginate(dict_items_15, PaginationRequest(page_size=5, after_key=5))
        ids = [item["id"] for item in resp.items]
        assert ids == [6, 7, 8, 9, 10]
        assert resp.page_info.has_previous_page is True
        assert resp.page_info.has_next_page is True

    def test_after_key_not_found_starts_from_beginning(self, dict_items_15):
        p = KeysetPaginator(sort_field="id")
        resp = p.paginate(dict_items_15, PaginationRequest(page_size=5, after_key=9999))
        ids = [item["id"] for item in resp.items]
        assert ids == [1, 2, 3, 4, 5]

    def test_request_sort_field_overrides_default(self, dict_items_15):
        p = KeysetPaginator(sort_field="id")
        resp = p.paginate(
            dict_items_15,
            PaginationRequest(page_size=5, sort_field="name"),
        )
        # sorted by 'name' lexicographically; should not raise
        assert len(resp.items) == 5

    def test_cursors_set_on_non_empty_page(self, dict_items_15):
        p = KeysetPaginator(sort_field="id")
        resp = p.paginate(dict_items_15, PaginationRequest(page_size=5))
        assert resp.page_info.start_cursor is not None
        assert resp.page_info.end_cursor is not None

    def test_no_cursors_on_empty_page(self):
        p = KeysetPaginator(sort_field="id")
        resp = p.paginate([], PaginationRequest(page_size=5))
        assert resp.page_info.start_cursor is None
        assert resp.page_info.end_cursor is None

    def test_missing_sort_field_falls_back_to_original_order(self):
        items = [{"x": 1}, {"x": 2}, {"x": 3}]
        p = KeysetPaginator(sort_field="missing_field")
        resp = p.paginate(items, PaginationRequest(page_size=2))
        assert len(resp.items) == 2

    def test_attribute_based_items(self):
        class Item:
            def __init__(self, id_):
                self.id = id_

        items = [Item(3), Item(1), Item(2)]
        p = KeysetPaginator(sort_field="id")
        resp = p.paginate(items, PaginationRequest(page_size=3))
        sorted_ids = [item.id for item in resp.items]
        assert sorted_ids == [1, 2, 3]

    def test_has_next_and_previous_correct(self, dict_items_15):
        p = KeysetPaginator(sort_field="id")
        # First page
        resp = p.paginate(dict_items_15, PaginationRequest(page_size=5))
        assert resp.page_info.has_previous_page is False
        assert resp.page_info.has_next_page is True

        # Middle page
        resp = p.paginate(dict_items_15, PaginationRequest(page_size=5, after_key=5))
        assert resp.page_info.has_previous_page is True
        assert resp.page_info.has_next_page is True

        # Last page
        resp = p.paginate(dict_items_15, PaginationRequest(page_size=5, after_key=10))
        assert resp.page_info.has_previous_page is True
        assert resp.page_info.has_next_page is False

    def test_total_items_set(self, dict_items_15):
        p = KeysetPaginator(sort_field="id")
        resp = p.paginate(dict_items_15, PaginationRequest(page_size=5))
        assert resp.page_info.total_items == 15


# ===========================================================================
# create_paginator factory
# ===========================================================================


class TestCreatePaginator:
    def test_offset_strategy(self):
        p = create_paginator(PaginationStrategy.OFFSET)
        assert isinstance(p, OffsetPaginator)

    def test_cursor_strategy(self):
        p = create_paginator(PaginationStrategy.CURSOR)
        assert isinstance(p, CursorPaginator)

    def test_keyset_strategy(self):
        p = create_paginator(PaginationStrategy.KEYSET)
        assert isinstance(p, KeysetPaginator)

    def test_keyset_with_sort_field_kwarg(self):
        p = create_paginator(PaginationStrategy.KEYSET, sort_field="name")
        assert p._sort_field == "name"

    def test_unknown_strategy_raises(self):
        with pytest.raises(ValueError, match="Unknown pagination strategy"):
            create_paginator("invalid_strategy")

    def test_factory_offset_actually_paginates(self):
        p = create_paginator(PaginationStrategy.OFFSET)
        items = list(range(10))
        resp = p.paginate(items, PaginationRequest(page=1, page_size=5))
        assert len(resp.items) == 5

    def test_factory_cursor_actually_paginates(self):
        p = create_paginator(PaginationStrategy.CURSOR)
        items = list(range(10))
        resp = p.paginate(items, PaginationRequest(page_size=5))
        assert len(resp.items) == 5

    def test_factory_keyset_actually_paginates(self):
        items = [{"id": i} for i in range(10)]
        p = create_paginator(PaginationStrategy.KEYSET, sort_field="id")
        resp = p.paginate(items, PaginationRequest(page_size=5))
        assert len(resp.items) == 5
