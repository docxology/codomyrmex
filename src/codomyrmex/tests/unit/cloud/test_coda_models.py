"""
Unit tests for Coda.io API data models — gap-filling suite.

Targets the 19 uncovered lines in models.py (96% → 100%) and exercises
every Enum value, every None-guard branch in from_dict(), and the
list pagination models not yet tested (PageList, TableList, ColumnList,
RowList, FormulaList, ControlList, PermissionList).

Zero-mock policy: no unittest.mock, MagicMock, or monkeypatch.
Pure data-model tests — no network required.
"""

import pytest


# ---------------------------------------------------------------------------
# Enum exhaustive coverage
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestTableTypeEnum:
    """All TableType enum values are reachable and carry correct string values."""

    def test_table_type_table(self):
        from codomyrmex.cloud.coda_io.models import TableType
        assert TableType.TABLE.value == "table"

    def test_table_type_view(self):
        from codomyrmex.cloud.coda_io.models import TableType
        assert TableType.VIEW.value == "view"

    def test_table_type_membership(self):
        from codomyrmex.cloud.coda_io.models import TableType
        members = {t.value for t in TableType}
        assert members == {"table", "view"}


@pytest.mark.unit
class TestPageTypeEnum:
    """All PageType enum values are reachable."""

    def test_canvas(self):
        from codomyrmex.cloud.coda_io.models import PageType
        assert PageType.CANVAS.value == "canvas"

    def test_embed(self):
        from codomyrmex.cloud.coda_io.models import PageType
        assert PageType.EMBED.value == "embed"

    def test_sync_page(self):
        from codomyrmex.cloud.coda_io.models import PageType
        assert PageType.SYNC_PAGE.value == "syncPage"

    def test_all_values(self):
        from codomyrmex.cloud.coda_io.models import PageType
        values = {pt.value for pt in PageType}
        assert values == {"canvas", "embed", "syncPage"}


@pytest.mark.unit
class TestControlTypeEnum:
    """All 14 ControlType enum values are defined and reachable."""

    def test_ai_block(self):
        from codomyrmex.cloud.coda_io.models import ControlType
        assert ControlType.AI_BLOCK.value == "aiBlock"

    def test_button(self):
        from codomyrmex.cloud.coda_io.models import ControlType
        assert ControlType.BUTTON.value == "button"

    def test_checkbox(self):
        from codomyrmex.cloud.coda_io.models import ControlType
        assert ControlType.CHECKBOX.value == "checkbox"

    def test_date_picker(self):
        from codomyrmex.cloud.coda_io.models import ControlType
        assert ControlType.DATE_PICKER.value == "datePicker"

    def test_date_range_picker(self):
        from codomyrmex.cloud.coda_io.models import ControlType
        assert ControlType.DATE_RANGE_PICKER.value == "dateRangePicker"

    def test_date_time_picker(self):
        from codomyrmex.cloud.coda_io.models import ControlType
        assert ControlType.DATE_TIME_PICKER.value == "dateTimePicker"

    def test_lookup(self):
        from codomyrmex.cloud.coda_io.models import ControlType
        assert ControlType.LOOKUP.value == "lookup"

    def test_multiselect(self):
        from codomyrmex.cloud.coda_io.models import ControlType
        assert ControlType.MULTISELECT.value == "multiselect"

    def test_select(self):
        from codomyrmex.cloud.coda_io.models import ControlType
        assert ControlType.SELECT.value == "select"

    def test_scale(self):
        from codomyrmex.cloud.coda_io.models import ControlType
        assert ControlType.SCALE.value == "scale"

    def test_slider(self):
        from codomyrmex.cloud.coda_io.models import ControlType
        assert ControlType.SLIDER.value == "slider"

    def test_reaction(self):
        from codomyrmex.cloud.coda_io.models import ControlType
        assert ControlType.REACTION.value == "reaction"

    def test_textbox(self):
        from codomyrmex.cloud.coda_io.models import ControlType
        assert ControlType.TEXTBOX.value == "textbox"

    def test_time_picker(self):
        from codomyrmex.cloud.coda_io.models import ControlType
        assert ControlType.TIME_PICKER.value == "timePicker"

    def test_total_count(self):
        from codomyrmex.cloud.coda_io.models import ControlType
        assert len(list(ControlType)) == 14


@pytest.mark.unit
class TestAccessTypeEnum:
    """All AccessType enum values are reachable."""

    def test_none(self):
        from codomyrmex.cloud.coda_io.models import AccessType
        assert AccessType.NONE.value == "none"

    def test_readonly(self):
        from codomyrmex.cloud.coda_io.models import AccessType
        assert AccessType.READONLY.value == "readonly"

    def test_write(self):
        from codomyrmex.cloud.coda_io.models import AccessType
        assert AccessType.WRITE.value == "write"

    def test_comment(self):
        from codomyrmex.cloud.coda_io.models import AccessType
        assert AccessType.COMMENT.value == "comment"


@pytest.mark.unit
class TestDocPublishModeEnum:
    """All DocPublishMode values are reachable."""

    def test_view(self):
        from codomyrmex.cloud.coda_io.models import DocPublishMode
        assert DocPublishMode.VIEW.value == "view"

    def test_play(self):
        from codomyrmex.cloud.coda_io.models import DocPublishMode
        assert DocPublishMode.PLAY.value == "play"

    def test_edit(self):
        from codomyrmex.cloud.coda_io.models import DocPublishMode
        assert DocPublishMode.EDIT.value == "edit"


@pytest.mark.unit
class TestValueFormatEnum:
    """All ValueFormat enum values are reachable."""

    def test_simple(self):
        from codomyrmex.cloud.coda_io.models import ValueFormat
        assert ValueFormat.SIMPLE.value == "simple"

    def test_simple_with_arrays(self):
        from codomyrmex.cloud.coda_io.models import ValueFormat
        assert ValueFormat.SIMPLE_WITH_ARRAYS.value == "simpleWithArrays"

    def test_rich(self):
        from codomyrmex.cloud.coda_io.models import ValueFormat
        assert ValueFormat.RICH.value == "rich"


# ---------------------------------------------------------------------------
# None-guard branches in from_dict() — the 19 uncovered lines
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestIconNoneGuard:
    """Icon.from_dict(None) returns None — covers line 89."""

    def test_from_dict_none(self):
        from codomyrmex.cloud.coda_io.models import Icon
        result = Icon.from_dict(None)
        assert result is None

    def test_from_dict_empty_dict(self):
        from codomyrmex.cloud.coda_io.models import Icon
        result = Icon.from_dict({})
        assert result is None

    def test_from_dict_full(self):
        from codomyrmex.cloud.coda_io.models import Icon
        icon = Icon.from_dict({"name": "star", "type": "builtin", "browserLink": "https://x.com/star.png"})
        assert icon is not None
        assert icon.name == "star"
        assert icon.type == "builtin"
        assert icon.browser_link == "https://x.com/star.png"

    def test_from_dict_partial(self):
        from codomyrmex.cloud.coda_io.models import Icon
        icon = Icon.from_dict({"name": "check"})
        assert icon is not None
        assert icon.name == "check"
        assert icon.type is None
        assert icon.browser_link is None


@pytest.mark.unit
class TestImageNoneGuard:
    """Image.from_dict(None) returns None — covers line 109."""

    def test_from_dict_none(self):
        from codomyrmex.cloud.coda_io.models import Image
        result = Image.from_dict(None)
        assert result is None

    def test_from_dict_empty_dict(self):
        from codomyrmex.cloud.coda_io.models import Image
        result = Image.from_dict({})
        assert result is None

    def test_from_dict_full(self):
        from codomyrmex.cloud.coda_io.models import Image
        image = Image.from_dict({
            "browserLink": "https://example.com/img.png",
            "type": "image/png",
            "width": 800,
            "height": 600,
        })
        assert image is not None
        assert image.browser_link == "https://example.com/img.png"
        assert image.width == 800
        assert image.height == 600

    def test_from_dict_dimensions_none(self):
        from codomyrmex.cloud.coda_io.models import Image
        image = Image.from_dict({"browserLink": "https://x.com/img.png"})
        assert image is not None
        assert image.width is None
        assert image.height is None


@pytest.mark.unit
class TestWorkspaceReferenceNoneGuard:
    """WorkspaceReference.from_dict(None) returns None — covers line 174."""

    def test_from_dict_none(self):
        from codomyrmex.cloud.coda_io.models import WorkspaceReference
        result = WorkspaceReference.from_dict(None)
        assert result is None

    def test_from_dict_empty(self):
        from codomyrmex.cloud.coda_io.models import WorkspaceReference
        result = WorkspaceReference.from_dict({})
        assert result is None

    def test_from_dict_full(self):
        from codomyrmex.cloud.coda_io.models import WorkspaceReference
        ws = WorkspaceReference.from_dict({
            "id": "ws-abc",
            "type": "workspace",
            "name": "Acme Corp",
            "organizationId": "org-123",
            "browserLink": "https://coda.io/w/ws-abc",
        })
        assert ws is not None
        assert ws.id == "ws-abc"
        assert ws.name == "Acme Corp"
        assert ws.organization_id == "org-123"
        assert ws.browser_link == "https://coda.io/w/ws-abc"

    def test_from_dict_defaults(self):
        from codomyrmex.cloud.coda_io.models import WorkspaceReference
        ws = WorkspaceReference.from_dict({"id": "ws-xyz"})
        assert ws is not None
        assert ws.type == "workspace"
        assert ws.name is None
        assert ws.organization_id is None


@pytest.mark.unit
class TestFolderReferenceNoneGuard:
    """FolderReference.from_dict(None) returns None — covers line 220."""

    def test_from_dict_none(self):
        from codomyrmex.cloud.coda_io.models import FolderReference
        result = FolderReference.from_dict(None)
        assert result is None

    def test_from_dict_empty(self):
        from codomyrmex.cloud.coda_io.models import FolderReference
        result = FolderReference.from_dict({})
        assert result is None

    def test_from_dict_full(self):
        from codomyrmex.cloud.coda_io.models import FolderReference
        folder = FolderReference.from_dict({
            "id": "fl-xyz",
            "type": "folder",
            "name": "Projects",
            "browserLink": "https://coda.io/f/fl-xyz",
        })
        assert folder is not None
        assert folder.id == "fl-xyz"
        assert folder.name == "Projects"
        assert folder.browser_link == "https://coda.io/f/fl-xyz"

    def test_from_dict_defaults(self):
        from codomyrmex.cloud.coda_io.models import FolderReference
        folder = FolderReference.from_dict({"id": "fl-abc"})
        assert folder is not None
        assert folder.type == "folder"
        assert folder.name is None


@pytest.mark.unit
class TestDocSizeNoneGuard:
    """DocSize.from_dict(None) returns None."""

    def test_from_dict_none(self):
        from codomyrmex.cloud.coda_io.models import DocSize
        result = DocSize.from_dict(None)
        assert result is None

    def test_from_dict_empty(self):
        from codomyrmex.cloud.coda_io.models import DocSize
        result = DocSize.from_dict({})
        assert result is None

    def test_from_dict_full(self):
        from codomyrmex.cloud.coda_io.models import DocSize
        size = DocSize.from_dict({
            "totalRowCount": 1000,
            "tableAndViewCount": 5,
            "pageCount": 20,
            "overApiSizeLimit": True,
        })
        assert size is not None
        assert size.total_row_count == 1000
        assert size.table_and_view_count == 5
        assert size.page_count == 20
        assert size.over_api_size_limit is True

    def test_from_dict_defaults(self):
        from codomyrmex.cloud.coda_io.models import DocSize
        # Non-empty dict but missing all keys — should use defaults
        size = DocSize.from_dict({"extra": "field"})
        assert size is not None
        assert size.total_row_count == 0
        assert size.over_api_size_limit is False


@pytest.mark.unit
class TestPageReferenceNoneGuard:
    """PageReference.from_dict(None) returns None — covers line 242."""

    def test_from_dict_none(self):
        from codomyrmex.cloud.coda_io.models import PageReference
        result = PageReference.from_dict(None)
        assert result is None

    def test_from_dict_empty(self):
        from codomyrmex.cloud.coda_io.models import PageReference
        result = PageReference.from_dict({})
        assert result is None

    def test_from_dict_full(self):
        from codomyrmex.cloud.coda_io.models import PageReference
        ref = PageReference.from_dict({
            "id": "canvas-abc",
            "type": "page",
            "href": "https://coda.io/apis/v1/docs/d/pages/canvas-abc",
            "browserLink": "https://coda.io/d/_d/Page_s123",
            "name": "My Page",
        })
        assert ref is not None
        assert ref.id == "canvas-abc"
        assert ref.name == "My Page"
        assert ref.href is not None

    def test_from_dict_defaults(self):
        from codomyrmex.cloud.coda_io.models import PageReference
        ref = PageReference.from_dict({"id": "canvas-xyz"})
        assert ref is not None
        assert ref.type == "page"
        assert ref.href is None
        assert ref.name is None


@pytest.mark.unit
class TestTableReferenceNoneGuard:
    """TableReference.from_dict(None) returns None."""

    def test_from_dict_none(self):
        from codomyrmex.cloud.coda_io.models import TableReference
        result = TableReference.from_dict(None)
        assert result is None

    def test_from_dict_empty(self):
        from codomyrmex.cloud.coda_io.models import TableReference
        result = TableReference.from_dict({})
        assert result is None

    def test_from_dict_full(self):
        from codomyrmex.cloud.coda_io.models import TableReference
        ref = TableReference.from_dict({
            "id": "grid-abc",
            "type": "table",
            "tableType": "view",
            "href": "https://coda.io/apis/v1/docs/d/tables/grid-abc",
            "browserLink": "https://coda.io/d/_d/#grid-abc",
            "name": "Tasks View",
        })
        assert ref is not None
        assert ref.id == "grid-abc"
        assert ref.table_type == "view"
        assert ref.name == "Tasks View"

    def test_from_dict_defaults(self):
        from codomyrmex.cloud.coda_io.models import TableReference
        ref = TableReference.from_dict({"id": "grid-xyz"})
        assert ref is not None
        assert ref.type == "table"
        assert ref.table_type is None
        assert ref.href is None


@pytest.mark.unit
class TestColumnReferenceNoneGuard:
    """ColumnReference.from_dict(None) returns None."""

    def test_from_dict_none(self):
        from codomyrmex.cloud.coda_io.models import ColumnReference
        result = ColumnReference.from_dict(None)
        assert result is None

    def test_from_dict_empty(self):
        from codomyrmex.cloud.coda_io.models import ColumnReference
        result = ColumnReference.from_dict({})
        assert result is None

    def test_from_dict_full(self):
        from codomyrmex.cloud.coda_io.models import ColumnReference
        ref = ColumnReference.from_dict({
            "id": "c-abc",
            "type": "column",
            "href": "https://coda.io/apis/v1/docs/d/tables/t/columns/c-abc",
        })
        assert ref is not None
        assert ref.id == "c-abc"
        assert ref.href is not None

    def test_from_dict_defaults(self):
        from codomyrmex.cloud.coda_io.models import ColumnReference
        ref = ColumnReference.from_dict({"id": "c-xyz"})
        assert ref is not None
        assert ref.type == "column"
        assert ref.href is None


@pytest.mark.unit
class TestPersonValueNoneGuard:
    """PersonValue.from_dict(None) returns None — covers line 328."""

    def test_from_dict_none(self):
        from codomyrmex.cloud.coda_io.models import PersonValue
        result = PersonValue.from_dict(None)
        assert result is None

    def test_from_dict_empty(self):
        from codomyrmex.cloud.coda_io.models import PersonValue
        result = PersonValue.from_dict({})
        assert result is None

    def test_from_dict_with_name_and_email(self):
        from codomyrmex.cloud.coda_io.models import PersonValue
        person = PersonValue.from_dict({"name": "Alice", "email": "alice@example.com"})
        assert person is not None
        assert person.name == "Alice"
        assert person.email == "alice@example.com"

    def test_from_dict_name_only(self):
        from codomyrmex.cloud.coda_io.models import PersonValue
        person = PersonValue.from_dict({"name": "Bob"})
        assert person is not None
        assert person.name == "Bob"
        assert person.email is None


# ---------------------------------------------------------------------------
# Pagination list models not previously tested
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestPageListModel:
    """PageList.from_dict correctly builds a list of pages — covers line 398."""

    def test_empty_list(self):
        from codomyrmex.cloud.coda_io.models import PageList
        result = PageList.from_dict({"items": []})
        assert result.items == []
        assert result.href is None
        assert result.next_page_token is None
        assert result.next_page_link is None

    def test_single_page(self):
        from codomyrmex.cloud.coda_io.models import PageList
        data = {
            "items": [
                {
                    "id": "canvas-abc",
                    "type": "page",
                    "href": "https://coda.io/apis/v1/docs/d/pages/canvas-abc",
                    "name": "Overview",
                    "isHidden": False,
                    "isEffectivelyHidden": False,
                    "browserLink": "https://coda.io/d/_d/Overview_s123",
                    "children": [],
                    "contentType": "canvas",
                }
            ],
            "href": "https://coda.io/apis/v1/docs/d/pages",
            "nextPageToken": "tok-abc",
            "nextPageLink": "https://coda.io/apis/v1/docs/d/pages?pageToken=tok-abc",
        }
        result = PageList.from_dict(data)
        assert len(result.items) == 1
        assert result.items[0].id == "canvas-abc"
        assert result.next_page_token == "tok-abc"
        assert result.href is not None

    def test_two_pages(self):
        from codomyrmex.cloud.coda_io.models import PageList

        def _make_page(page_id: str, name: str) -> dict:
            return {
                "id": page_id,
                "type": "page",
                "href": f"https://coda.io/apis/v1/docs/d/pages/{page_id}",
                "name": name,
                "isHidden": False,
                "isEffectivelyHidden": False,
                "browserLink": f"https://coda.io/d/_d/{name}_s123",
                "children": [],
                "contentType": "canvas",
            }

        data = {"items": [_make_page("p1", "Page One"), _make_page("p2", "Page Two")]}
        result = PageList.from_dict(data)
        assert len(result.items) == 2
        assert result.items[0].name == "Page One"
        assert result.items[1].name == "Page Two"


@pytest.mark.unit
class TestPageContentItemModel:
    """PageContentItem.from_dict correctly maps fields — covers line 416."""

    def test_minimal(self):
        from codomyrmex.cloud.coda_io.models import PageContentItem
        item = PageContentItem.from_dict({"id": "item-1", "type": "paragraph"})
        assert item.id == "item-1"
        assert item.type == "paragraph"
        assert item.text is None

    def test_with_text(self):
        from codomyrmex.cloud.coda_io.models import PageContentItem
        item = PageContentItem.from_dict({"id": "item-2", "type": "heading", "text": "Hello World"})
        assert item.text == "Hello World"

    def test_empty_defaults(self):
        from codomyrmex.cloud.coda_io.models import PageContentItem
        item = PageContentItem.from_dict({})
        assert item.id == ""
        assert item.type == ""


@pytest.mark.unit
class TestSortModel:
    """Sort.from_dict handles column reference correctly — covers line 432."""

    def test_with_column_data(self):
        from codomyrmex.cloud.coda_io.models import Sort
        data = {
            "column": {"id": "c-name", "type": "column", "href": "https://coda.io/col/c-name"},
            "direction": "ascending",
        }
        sort = Sort.from_dict(data)
        assert sort.column.id == "c-name"
        assert sort.direction == "ascending"

    def test_descending_direction(self):
        from codomyrmex.cloud.coda_io.models import Sort
        data = {
            "column": {"id": "c-date", "type": "column"},
            "direction": "descending",
        }
        sort = Sort.from_dict(data)
        assert sort.direction == "descending"

    def test_missing_column_falls_back_to_empty_reference(self):
        from codomyrmex.cloud.coda_io.models import Sort
        # ColumnReference.from_dict(None) returns None; Sort uses empty fallback
        sort = Sort.from_dict({"direction": "ascending"})
        assert sort.column.id == ""
        assert sort.direction == "ascending"

    def test_default_direction(self):
        from codomyrmex.cloud.coda_io.models import Sort
        sort = Sort.from_dict({"column": {"id": "c-x"}})
        assert sort.direction == "ascending"


@pytest.mark.unit
class TestTableListModel:
    """TableList.from_dict correctly builds list of tables — covers line 493."""

    def test_empty_list(self):
        from codomyrmex.cloud.coda_io.models import TableList
        result = TableList.from_dict({"items": []})
        assert result.items == []
        assert result.href is None

    def test_two_tables(self):
        from codomyrmex.cloud.coda_io.models import TableList

        def _make_table(table_id: str, name: str) -> dict:
            return {
                "id": table_id,
                "type": "table",
                "tableType": "table",
                "href": f"https://coda.io/apis/v1/docs/d/tables/{table_id}",
                "name": name,
                "browserLink": f"https://coda.io/d/_d/#{name}_{table_id}",
                "rowCount": 10,
                "layout": "default",
            }

        data = {
            "items": [_make_table("grid-1", "Alpha"), _make_table("grid-2", "Beta")],
            "href": "https://coda.io/apis/v1/docs/d/tables",
            "nextPageToken": None,
        }
        result = TableList.from_dict(data)
        assert len(result.items) == 2
        assert result.items[0].name == "Alpha"
        assert result.items[1].name == "Beta"

    def test_pagination_fields(self):
        from codomyrmex.cloud.coda_io.models import TableList
        data = {
            "items": [],
            "href": "https://coda.io/apis/v1/docs/d/tables",
            "nextPageToken": "tok-xyz",
            "nextPageLink": "https://coda.io/apis/v1/docs/d/tables?pageToken=tok-xyz",
        }
        result = TableList.from_dict(data)
        assert result.next_page_token == "tok-xyz"
        assert result.next_page_link is not None


@pytest.mark.unit
class TestColumnListModel:
    """ColumnList.from_dict correctly builds list of columns — covers line 543."""

    def test_empty_list(self):
        from codomyrmex.cloud.coda_io.models import ColumnList
        result = ColumnList.from_dict({"items": []})
        assert result.items == []

    def test_single_column(self):
        from codomyrmex.cloud.coda_io.models import ColumnList
        data = {
            "items": [
                {
                    "id": "c-status",
                    "type": "column",
                    "href": "https://coda.io/col/c-status",
                    "name": "Status",
                    "format": {"type": "select"},
                }
            ]
        }
        result = ColumnList.from_dict(data)
        assert len(result.items) == 1
        assert result.items[0].name == "Status"

    def test_pagination_none(self):
        from codomyrmex.cloud.coda_io.models import ColumnList
        result = ColumnList.from_dict({"items": []})
        assert result.next_page_token is None
        assert result.next_page_link is None


@pytest.mark.unit
class TestRowListModel:
    """RowList.from_dict builds list of rows, including next_sync_token — covers line 594."""

    def test_empty_list(self):
        from codomyrmex.cloud.coda_io.models import RowList
        result = RowList.from_dict({"items": []})
        assert result.items == []
        assert result.next_sync_token is None

    def test_with_sync_token(self):
        from codomyrmex.cloud.coda_io.models import RowList
        data = {
            "items": [],
            "href": "https://coda.io/rows",
            "nextSyncToken": "sync-abc-123",
        }
        result = RowList.from_dict(data)
        assert result.next_sync_token == "sync-abc-123"

    def test_two_rows(self):
        from codomyrmex.cloud.coda_io.models import RowList

        def _make_row(row_id: str, idx: int) -> dict:
            return {
                "id": row_id,
                "type": "row",
                "href": f"https://coda.io/row/{row_id}",
                "name": f"Row {idx}",
                "index": idx,
                "browserLink": f"https://coda.io/d/_d#_{row_id}",
                "values": {"col1": f"val{idx}"},
            }

        data = {"items": [_make_row("r-1", 0), _make_row("r-2", 1)]}
        result = RowList.from_dict(data)
        assert len(result.items) == 2
        assert result.items[0].index == 0
        assert result.items[1].index == 1


@pytest.mark.unit
class TestFormulaModel:
    """Formula.from_dict covers basic path — covers line 639."""

    def test_minimal(self):
        from codomyrmex.cloud.coda_io.models import Formula
        data = {
            "id": "f-abc",
            "type": "formula",
            "href": "https://coda.io/formula/f-abc",
            "name": "TotalRevenue",
            "value": 42000,
        }
        formula = Formula.from_dict(data)
        assert formula.id == "f-abc"
        assert formula.name == "TotalRevenue"
        assert formula.value == 42000
        assert formula.parent is None

    def test_with_parent(self):
        from codomyrmex.cloud.coda_io.models import Formula
        data = {
            "id": "f-xyz",
            "type": "formula",
            "href": "https://coda.io/formula/f-xyz",
            "name": "Count",
            "value": 100,
            "parent": {"id": "canvas-p", "type": "page", "name": "Stats"},
        }
        formula = Formula.from_dict(data)
        assert formula.parent is not None
        assert formula.parent.id == "canvas-p"

    def test_string_value(self):
        from codomyrmex.cloud.coda_io.models import Formula
        data = {
            "id": "f-str",
            "type": "formula",
            "href": "https://coda.io/formula/f-str",
            "name": "Status",
            "value": "active",
        }
        formula = Formula.from_dict(data)
        assert formula.value == "active"

    def test_defaults(self):
        from codomyrmex.cloud.coda_io.models import Formula
        formula = Formula.from_dict({})
        assert formula.id == ""
        assert formula.type == "formula"
        assert formula.value is None


@pytest.mark.unit
class TestFormulaListModel:
    """FormulaList.from_dict builds list — covers line 660."""

    def test_empty(self):
        from codomyrmex.cloud.coda_io.models import FormulaList
        result = FormulaList.from_dict({"items": []})
        assert result.items == []
        assert result.href is None

    def test_two_formulas(self):
        from codomyrmex.cloud.coda_io.models import FormulaList

        def _f(fid: str, name: str) -> dict:
            return {"id": fid, "type": "formula", "href": f"https://x/{fid}", "name": name, "value": 1}

        result = FormulaList.from_dict({"items": [_f("f1", "Alpha"), _f("f2", "Beta")]})
        assert len(result.items) == 2
        assert result.items[1].name == "Beta"

    def test_pagination_fields(self):
        from codomyrmex.cloud.coda_io.models import FormulaList
        data = {
            "items": [],
            "href": "https://coda.io/formulas",
            "nextPageToken": "pgT",
            "nextPageLink": "https://coda.io/formulas?pt=pgT",
        }
        result = FormulaList.from_dict(data)
        assert result.next_page_token == "pgT"
        assert result.next_page_link is not None


@pytest.mark.unit
class TestControlModel:
    """Control.from_dict — covers line 682."""

    def test_minimal(self):
        from codomyrmex.cloud.coda_io.models import Control
        data = {
            "id": "ctrl-1",
            "type": "control",
            "href": "https://coda.io/ctrl/ctrl-1",
            "name": "Filter",
            "controlType": "select",
            "value": "Active",
        }
        ctrl = Control.from_dict(data)
        assert ctrl.id == "ctrl-1"
        assert ctrl.control_type == "select"
        assert ctrl.value == "Active"
        assert ctrl.parent is None

    def test_with_parent(self):
        from codomyrmex.cloud.coda_io.models import Control
        data = {
            "id": "ctrl-2",
            "type": "control",
            "href": "https://coda.io/ctrl/ctrl-2",
            "name": "Toggle",
            "controlType": "checkbox",
            "value": True,
            "parent": {"id": "canvas-x", "type": "page", "name": "Dashboard"},
        }
        ctrl = Control.from_dict(data)
        assert ctrl.parent is not None
        assert ctrl.parent.name == "Dashboard"

    def test_defaults(self):
        from codomyrmex.cloud.coda_io.models import Control
        ctrl = Control.from_dict({})
        assert ctrl.id == ""
        assert ctrl.type == "control"
        assert ctrl.control_type == ""
        assert ctrl.value is None


@pytest.mark.unit
class TestControlListModel:
    """ControlList.from_dict builds list — covers line 704."""

    def test_empty(self):
        from codomyrmex.cloud.coda_io.models import ControlList
        result = ControlList.from_dict({"items": []})
        assert result.items == []

    def test_two_controls(self):
        from codomyrmex.cloud.coda_io.models import ControlList

        def _c(cid: str, name: str) -> dict:
            return {
                "id": cid,
                "type": "control",
                "href": f"https://x/{cid}",
                "name": name,
                "controlType": "button",
                "value": None,
            }

        result = ControlList.from_dict({"items": [_c("c1", "Run"), _c("c2", "Reset")]})
        assert len(result.items) == 2
        assert result.items[0].name == "Run"


@pytest.mark.unit
class TestPrincipalModel:
    """Principal.from_dict and to_dict — covers line 725 (anonymous principal)."""

    def test_email_principal(self):
        from codomyrmex.cloud.coda_io.models import Principal
        p = Principal.from_dict({"type": "email", "email": "user@example.com"})
        assert p.type == "email"
        assert p.email == "user@example.com"

    def test_domain_principal(self):
        from codomyrmex.cloud.coda_io.models import Principal
        p = Principal.from_dict({"type": "domain"})
        assert p.type == "domain"
        assert p.email is None

    def test_anyone_principal(self):
        from codomyrmex.cloud.coda_io.models import Principal
        p = Principal.from_dict({"type": "anyone"})
        assert p.type == "anyone"
        assert p.email is None

    def test_to_dict_with_email(self):
        from codomyrmex.cloud.coda_io.models import Principal
        p = Principal(type="email", email="dev@example.com")
        d = p.to_dict()
        assert d["type"] == "email"
        assert d["email"] == "dev@example.com"

    def test_to_dict_without_email(self):
        """to_dict omits email key when email is None — covers conditional branch line 725."""
        from codomyrmex.cloud.coda_io.models import Principal
        p = Principal(type="anyone", email=None)
        d = p.to_dict()
        assert d == {"type": "anyone"}
        assert "email" not in d

    def test_defaults_from_empty_dict(self):
        from codomyrmex.cloud.coda_io.models import Principal
        p = Principal.from_dict({})
        assert p.type == ""
        assert p.email is None


@pytest.mark.unit
class TestPermissionModel:
    """Permission.from_dict — covers line 749."""

    def test_full(self):
        from codomyrmex.cloud.coda_io.models import Permission
        data = {
            "id": "perm-1",
            "principal": {"type": "email", "email": "alice@example.com"},
            "access": "readonly",
        }
        perm = Permission.from_dict(data)
        assert perm.id == "perm-1"
        assert perm.principal.email == "alice@example.com"
        assert perm.access == "readonly"

    def test_write_access(self):
        from codomyrmex.cloud.coda_io.models import Permission
        data = {
            "id": "perm-2",
            "principal": {"type": "domain"},
            "access": "write",
        }
        perm = Permission.from_dict(data)
        assert perm.access == "write"
        assert perm.principal.type == "domain"

    def test_defaults(self):
        from codomyrmex.cloud.coda_io.models import Permission
        perm = Permission.from_dict({"principal": {}})
        assert perm.id == ""
        assert perm.access == ""


@pytest.mark.unit
class TestPermissionListModel:
    """PermissionList.from_dict — covers line 767."""

    def test_empty(self):
        from codomyrmex.cloud.coda_io.models import PermissionList
        result = PermissionList.from_dict({"items": [], "href": "https://coda.io/perms"})
        assert result.items == []
        assert result.href == "https://coda.io/perms"
        assert result.next_page_token is None

    def test_single_permission(self):
        from codomyrmex.cloud.coda_io.models import PermissionList
        data = {
            "items": [
                {
                    "id": "perm-a",
                    "principal": {"type": "email", "email": "bob@example.com"},
                    "access": "comment",
                }
            ],
            "href": "https://coda.io/perms",
        }
        result = PermissionList.from_dict(data)
        assert len(result.items) == 1
        assert result.items[0].principal.email == "bob@example.com"
        assert result.items[0].access == "comment"

    def test_pagination_fields(self):
        from codomyrmex.cloud.coda_io.models import PermissionList
        data = {
            "items": [],
            "href": "https://coda.io/perms",
            "nextPageToken": "pT",
            "nextPageLink": "https://coda.io/perms?pt=pT",
        }
        result = PermissionList.from_dict(data)
        assert result.next_page_token == "pT"
        assert result.next_page_link is not None


# ---------------------------------------------------------------------------
# Doc with all optional nested objects populated
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestDocWithAllOptionals:
    """Doc.from_dict with icon, doc_size, source_doc, published all set."""

    def test_doc_with_icon(self):
        from codomyrmex.cloud.coda_io.models import Doc
        data = {
            "id": "AbCDeFGH",
            "type": "doc",
            "href": "https://coda.io/apis/v1/docs/AbCDeFGH",
            "browserLink": "https://coda.io/d/_dAbCDeFGH",
            "name": "Full Doc",
            "owner": "user@example.com",
            "ownerName": "Test User",
            "icon": {"name": "rocket", "type": "builtin", "browserLink": "https://coda.io/icons/rocket.png"},
            "docSize": {
                "totalRowCount": 500,
                "tableAndViewCount": 3,
                "pageCount": 10,
                "overApiSizeLimit": False,
            },
            "sourceDoc": {"id": "src-doc-id"},
            "published": {"mode": "view"},
        }
        doc = Doc.from_dict(data)
        assert doc.icon is not None
        assert doc.icon.name == "rocket"
        assert doc.doc_size is not None
        assert doc.doc_size.total_row_count == 500
        assert doc.source_doc == {"id": "src-doc-id"}
        assert doc.published == {"mode": "view"}

    def test_doc_deprecated_ids(self):
        from codomyrmex.cloud.coda_io.models import Doc
        data = {
            "id": "doc-dep",
            "type": "doc",
            "href": "https://coda.io/apis/v1/docs/doc-dep",
            "browserLink": "https://coda.io/d/_ddoc-dep",
            "name": "Deprecated Fields Doc",
            "owner": "user@example.com",
            "ownerName": "User",
            "workspaceId": "ws-deprecated",
            "folderId": "fl-deprecated",
        }
        doc = Doc.from_dict(data)
        assert doc.workspace_id == "ws-deprecated"
        assert doc.folder_id == "fl-deprecated"


# ---------------------------------------------------------------------------
# Page with all optional fields
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestPageWithAllOptionals:
    """Page.from_dict with authors, icon, image, parent, created_by, updated_by all set."""

    def test_page_with_full_metadata(self):
        from codomyrmex.cloud.coda_io.models import Page
        data = {
            "id": "canvas-full",
            "type": "page",
            "href": "https://coda.io/apis/v1/docs/d/pages/canvas-full",
            "name": "Full Page",
            "isHidden": True,
            "isEffectivelyHidden": True,
            "browserLink": "https://coda.io/d/_d/Full_sfull",
            "children": [],
            "contentType": "embed",
            "subtitle": "A page with everything",
            "icon": {"name": "fire", "type": "builtin"},
            "image": {"browserLink": "https://example.com/cover.jpg", "width": 1200, "height": 630},
            "parent": {"id": "canvas-parent", "type": "page", "name": "Parent"},
            "authors": [
                {"name": "Alice", "email": "alice@example.com"},
                {"name": "Bob", "email": "bob@example.com"},
            ],
            "createdAt": "2024-03-01T09:00:00Z",
            "createdBy": {"name": "Alice", "email": "alice@example.com"},
            "updatedAt": "2024-03-02T10:00:00Z",
            "updatedBy": {"name": "Bob", "email": "bob@example.com"},
        }
        page = Page.from_dict(data)

        assert page.is_hidden is True
        assert page.is_effectively_hidden is True
        assert page.content_type == "embed"
        assert page.subtitle == "A page with everything"
        assert page.icon is not None
        assert page.icon.name == "fire"
        assert page.image is not None
        assert page.image.width == 1200
        assert page.parent is not None
        assert page.parent.id == "canvas-parent"
        assert page.authors is not None
        assert len(page.authors) == 2
        assert page.authors[0].name == "Alice"
        assert page.created_at is not None
        assert page.created_by is not None
        assert page.created_by.email == "alice@example.com"
        assert page.updated_by is not None
        assert page.updated_by.name == "Bob"

    def test_page_authors_empty_list(self):
        from codomyrmex.cloud.coda_io.models import Page
        data = {
            "id": "canvas-noauth",
            "type": "page",
            "href": "https://coda.io/p",
            "name": "No Authors",
            "isHidden": False,
            "isEffectivelyHidden": False,
            "browserLink": "https://coda.io/p",
            "children": [],
            "contentType": "canvas",
            "authors": [],
        }
        page = Page.from_dict(data)
        assert page.authors is None  # empty list → None per from_dict logic


# ---------------------------------------------------------------------------
# Table with sorts and nested parent
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestTableWithSortsAndParent:
    """Table.from_dict with sorts list and parent/parentTable populated."""

    def test_table_with_sorts(self):
        from codomyrmex.cloud.coda_io.models import Table
        data = {
            "id": "grid-sorted",
            "type": "table",
            "tableType": "table",
            "href": "https://coda.io/t/grid-sorted",
            "name": "Sorted Table",
            "browserLink": "https://coda.io/d/_d/#Sorted_tgrid-sorted",
            "rowCount": 50,
            "layout": "default",
            "sorts": [
                {"column": {"id": "c-due", "type": "column"}, "direction": "ascending"},
                {"column": {"id": "c-pri", "type": "column"}, "direction": "descending"},
            ],
            "parent": {"id": "canvas-p1", "type": "page", "name": "Status Page"},
            "parentTable": {"id": "grid-base", "type": "table", "tableType": "table"},
            "displayColumn": {"id": "c-name", "type": "column"},
            "filter": {"formula": "thisRow.Status == 'Active'"},
        }
        table = Table.from_dict(data)

        assert table.sorts is not None
        assert len(table.sorts) == 2
        assert table.sorts[0].column.id == "c-due"
        assert table.sorts[0].direction == "ascending"
        assert table.sorts[1].direction == "descending"
        assert table.parent is not None
        assert table.parent.name == "Status Page"
        assert table.parent_table is not None
        assert table.parent_table.id == "grid-base"
        assert table.display_column is not None
        assert table.display_column.id == "c-name"
        assert table.filter is not None

    def test_table_no_sorts(self):
        from codomyrmex.cloud.coda_io.models import Table
        data = {
            "id": "grid-nosorts",
            "type": "table",
            "tableType": "table",
            "href": "https://coda.io/t/grid-nosorts",
            "name": "Plain Table",
            "browserLink": "https://coda.io/d/_d/#plain",
            "rowCount": 5,
            "layout": "default",
        }
        table = Table.from_dict(data)
        assert table.sorts is None


# ---------------------------------------------------------------------------
# Row with parent table
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestRowWithParent:
    """Row.from_dict with parent TableReference populated."""

    def test_row_with_parent(self):
        from codomyrmex.cloud.coda_io.models import Row
        data = {
            "id": "r-abc",
            "type": "row",
            "href": "https://coda.io/row/r-abc",
            "name": "Row A",
            "index": 0,
            "browserLink": "https://coda.io/d/_d#_rr-abc",
            "values": {"c-col1": "hello"},
            "parent": {"id": "grid-parent", "type": "table", "tableType": "table"},
        }
        row = Row.from_dict(data)
        assert row.parent is not None
        assert row.parent.id == "grid-parent"

    def test_row_empty_values(self):
        from codomyrmex.cloud.coda_io.models import Row
        data = {
            "id": "r-empty",
            "type": "row",
            "href": "https://coda.io/row/r-empty",
            "name": "Empty Row",
            "index": 1,
            "browserLink": "https://coda.io/d/_d#_rr-empty",
            "values": {},
        }
        row = Row.from_dict(data)
        assert row.values == {}
        assert row.parent is None


# ---------------------------------------------------------------------------
# Column with parent
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestColumnWithParent:
    """Column.from_dict with parent TableReference populated."""

    def test_column_with_parent(self):
        from codomyrmex.cloud.coda_io.models import Column
        data = {
            "id": "c-name",
            "type": "column",
            "href": "https://coda.io/col/c-name",
            "name": "Name",
            "format": {"type": "text"},
            "display": True,
            "parent": {"id": "grid-abc", "type": "table", "tableType": "table", "name": "Tasks"},
        }
        col = Column.from_dict(data)
        assert col.display is True
        assert col.parent is not None
        assert col.parent.id == "grid-abc"

    def test_column_default_value(self):
        from codomyrmex.cloud.coda_io.models import Column
        data = {
            "id": "c-dv",
            "type": "column",
            "href": "https://coda.io/col/c-dv",
            "name": "Priority",
            "format": {"type": "select"},
            "defaultValue": "Medium",
        }
        col = Column.from_dict(data)
        assert col.default_value == "Medium"


# ---------------------------------------------------------------------------
# User without workspace / without pictureLink
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestUserWithoutOptionals:
    """User.from_dict with no workspace and no picture_link."""

    def test_user_minimal(self):
        from codomyrmex.cloud.coda_io.models import User
        data = {
            "name": "Jane Smith",
            "loginId": "jane@example.com",
            "type": "user",
            "scoped": True,
            "tokenName": "Read-Only Token",
            "href": "https://coda.io/apis/v1/whoami",
        }
        user = User.from_dict(data)
        assert user.name == "Jane Smith"
        assert user.scoped is True
        assert user.workspace is None
        assert user.picture_link is None

    def test_user_scoped_with_picture(self):
        from codomyrmex.cloud.coda_io.models import User
        data = {
            "name": "Dev Bot",
            "loginId": "bot@example.com",
            "type": "user",
            "scoped": True,
            "tokenName": "Bot Token",
            "href": "https://coda.io/apis/v1/whoami",
            "pictureLink": "https://cdn.coda.io/avatar/bot.png",
        }
        user = User.from_dict(data)
        assert user.picture_link == "https://cdn.coda.io/avatar/bot.png"


# ---------------------------------------------------------------------------
# InsertRowsResult edge cases
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestInsertRowsResultEdgeCases:
    """InsertRowsResult with no added_row_ids."""

    def test_no_row_ids(self):
        from codomyrmex.cloud.coda_io.models import InsertRowsResult
        result = InsertRowsResult.from_dict({"requestId": "req-xyz"})
        assert result.request_id == "req-xyz"
        assert result.added_row_ids is None

    def test_empty_row_ids(self):
        from codomyrmex.cloud.coda_io.models import InsertRowsResult
        result = InsertRowsResult.from_dict({"requestId": "req-abc", "addedRowIds": []})
        assert result.added_row_ids == []


# ---------------------------------------------------------------------------
# CellEdit with various value types
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestCellEditValueTypes:
    """CellEdit handles various value types including None, int, bool, list."""

    def test_none_value(self):
        from codomyrmex.cloud.coda_io.models import CellEdit
        cell = CellEdit(column="c-x", value=None)
        result = cell.to_dict()
        assert result == {"column": "c-x", "value": None}

    def test_int_value(self):
        from codomyrmex.cloud.coda_io.models import CellEdit
        cell = CellEdit(column="c-count", value=42)
        assert cell.to_dict() == {"column": "c-count", "value": 42}

    def test_bool_value(self):
        from codomyrmex.cloud.coda_io.models import CellEdit
        cell = CellEdit(column="c-done", value=True)
        assert cell.to_dict() == {"column": "c-done", "value": True}

    def test_list_value(self):
        from codomyrmex.cloud.coda_io.models import CellEdit
        cell = CellEdit(column="c-tags", value=["urgent", "review"])
        result = cell.to_dict()
        assert result["value"] == ["urgent", "review"]


# ---------------------------------------------------------------------------
# RowEdit with empty cells
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestRowEditEdgeCases:
    """RowEdit handles zero-cell and single-cell cases."""

    def test_empty_cells(self):
        from codomyrmex.cloud.coda_io.models import RowEdit
        row = RowEdit(cells=[])
        result = row.to_dict()
        assert result == {"cells": []}

    def test_single_cell(self):
        from codomyrmex.cloud.coda_io.models import CellEdit, RowEdit
        row = RowEdit(cells=[CellEdit(column="Status", value="Done")])
        result = row.to_dict()
        assert len(result["cells"]) == 1
        assert result["cells"][0]["column"] == "Status"


# ---------------------------------------------------------------------------
# _parse_datetime edge cases
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestParseDatetimeEdgeCases:
    """_parse_datetime handles various ISO 8601 edge cases."""

    def test_empty_string_returns_none(self):
        from codomyrmex.cloud.coda_io.models import _parse_datetime
        result = _parse_datetime("")
        assert result is None

    def test_datetime_without_timezone(self):
        from codomyrmex.cloud.coda_io.models import _parse_datetime
        result = _parse_datetime("2024-06-15T12:00:00")
        assert result is not None
        assert result.year == 2024
        assert result.month == 6
        assert result.day == 15

    def test_datetime_with_positive_offset(self):
        from codomyrmex.cloud.coda_io.models import _parse_datetime
        result = _parse_datetime("2024-01-01T08:00:00+05:30")
        assert result is not None
        assert result.year == 2024

    def test_z_suffix_converted_to_utc_offset(self):
        from codomyrmex.cloud.coda_io.models import _parse_datetime
        result = _parse_datetime("2024-12-31T23:59:59Z")
        assert result is not None
        assert result.year == 2024
        assert result.month == 12
        assert result.day == 31

    def test_type_error_returns_none(self):
        from codomyrmex.cloud.coda_io.models import _parse_datetime
        # Passing an integer where a string is expected — triggers TypeError
        result = _parse_datetime(12345)  # type: ignore[arg-type]
        assert result is None
