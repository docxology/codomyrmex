"""Comprehensive tests for cloud.coda_io.models — zero-stub.

Covers all enums, all reference types, all core resources, all pagination
list types, permissions, user, mutation results, and to_dict methods.
Uses real class instantiation only; no stubing.
"""

from codomyrmex.cloud.coda_io.models import (
    AccessType,
    ACLSettings,
    CellEdit,
    Column,
    ColumnList,
    ColumnReference,
    Control,
    ControlList,
    ControlType,
    Doc,
    DocList,
    DocPublishMode,
    DocSize,
    FolderReference,
    Formula,
    FormulaList,
    Icon,
    Image,
    InsertRowsResult,
    MutationStatus,
    Page,
    PageContentItem,
    PageList,
    PageReference,
    PageType,
    Permission,
    PermissionList,
    PersonValue,
    Principal,
    Row,
    RowEdit,
    RowList,
    SharingMetadata,
    Sort,
    Table,
    TableList,
    TableReference,
    TableType,
    User,
    ValueFormat,
    WorkspaceReference,
)

# ---------------------------------------------------------------------------
# Enums — every value individually tested
# ---------------------------------------------------------------------------


class TestTableTypeEnum:
    def test_table_value(self):
        assert TableType.TABLE.value == "table"

    def test_view_value(self):
        assert TableType.VIEW.value == "view"

    def test_member_count(self):
        assert len(TableType) == 2


class TestPageTypeEnum:
    def test_canvas_value(self):
        assert PageType.CANVAS.value == "canvas"

    def test_embed_value(self):
        assert PageType.EMBED.value == "embed"

    def test_sync_page_value(self):
        assert PageType.SYNC_PAGE.value == "syncPage"

    def test_member_count(self):
        assert len(PageType) == 3


class TestControlTypeEnum:
    def test_ai_block(self):
        assert ControlType.AI_BLOCK.value == "aiBlock"

    def test_button(self):
        assert ControlType.BUTTON.value == "button"

    def test_checkbox(self):
        assert ControlType.CHECKBOX.value == "checkbox"

    def test_date_picker(self):
        assert ControlType.DATE_PICKER.value == "datePicker"

    def test_date_range_picker(self):
        assert ControlType.DATE_RANGE_PICKER.value == "dateRangePicker"

    def test_date_time_picker(self):
        assert ControlType.DATE_TIME_PICKER.value == "dateTimePicker"

    def test_lookup(self):
        assert ControlType.LOOKUP.value == "lookup"

    def test_multiselect(self):
        assert ControlType.MULTISELECT.value == "multiselect"

    def test_select(self):
        assert ControlType.SELECT.value == "select"

    def test_scale(self):
        assert ControlType.SCALE.value == "scale"

    def test_slider(self):
        assert ControlType.SLIDER.value == "slider"

    def test_reaction(self):
        assert ControlType.REACTION.value == "reaction"

    def test_textbox(self):
        assert ControlType.TEXTBOX.value == "textbox"

    def test_time_picker(self):
        assert ControlType.TIME_PICKER.value == "timePicker"

    def test_member_count(self):
        assert len(ControlType) == 14


class TestAccessTypeEnum:
    def test_none_value(self):
        assert AccessType.NONE.value == "none"

    def test_readonly_value(self):
        assert AccessType.READONLY.value == "readonly"

    def test_write_value(self):
        assert AccessType.WRITE.value == "write"

    def test_comment_value(self):
        assert AccessType.COMMENT.value == "comment"

    def test_member_count(self):
        assert len(AccessType) == 4


class TestDocPublishModeEnum:
    def test_view_value(self):
        assert DocPublishMode.VIEW.value == "view"

    def test_play_value(self):
        assert DocPublishMode.PLAY.value == "play"

    def test_edit_value(self):
        assert DocPublishMode.EDIT.value == "edit"

    def test_member_count(self):
        assert len(DocPublishMode) == 3


class TestValueFormatEnum:
    def test_simple_value(self):
        assert ValueFormat.SIMPLE.value == "simple"

    def test_simple_with_arrays_value(self):
        assert ValueFormat.SIMPLE_WITH_ARRAYS.value == "simpleWithArrays"

    def test_rich_value(self):
        assert ValueFormat.RICH.value == "rich"

    def test_member_count(self):
        assert len(ValueFormat) == 3


# ---------------------------------------------------------------------------
# Icon
# ---------------------------------------------------------------------------


class TestIcon:
    def test_direct_construction(self):
        icon = Icon(name="star", type="emoji", browser_link="https://example.com/star")
        assert icon.name == "star"
        assert icon.type == "emoji"
        assert icon.browser_link == "https://example.com/star"

    def test_defaults_all_none(self):
        icon = Icon()
        assert icon.name is None
        assert icon.type is None
        assert icon.browser_link is None

    def test_from_dict_full(self):
        data = {
            "name": "folder",
            "type": "system",
            "browserLink": "https://coda.io/icon/folder",
        }
        icon = Icon.from_dict(data)
        assert icon is not None
        assert icon.name == "folder"
        assert icon.type == "system"
        assert icon.browser_link == "https://coda.io/icon/folder"

    def test_from_dict_maps_browser_link_camel_case(self):
        data = {"browserLink": "https://coda.io/icon/x"}
        icon = Icon.from_dict(data)
        assert icon is not None
        assert icon.browser_link == "https://coda.io/icon/x"

    def test_from_dict_partial(self):
        data = {"name": "bookmark"}
        icon = Icon.from_dict(data)
        assert icon is not None
        assert icon.name == "bookmark"
        assert icon.type is None
        assert icon.browser_link is None

    def test_from_dict_none_returns_none(self):
        assert Icon.from_dict(None) is None

    def test_from_dict_empty_dict_returns_none(self):
        # empty dict is falsy for `if not data`
        assert Icon.from_dict({}) is None


# ---------------------------------------------------------------------------
# Image
# ---------------------------------------------------------------------------


class TestImage:
    def test_direct_construction_with_dimensions(self):
        img = Image(
            browser_link="https://img.example.com/photo.jpg",
            type="image",
            width=1280,
            height=720,
        )
        assert img.width == 1280
        assert img.height == 720

    def test_defaults_all_none(self):
        img = Image()
        assert img.browser_link is None
        assert img.width is None
        assert img.height is None

    def test_from_dict_full(self):
        data = {
            "browserLink": "https://img.example.com/x.png",
            "type": "image",
            "width": 800,
            "height": 600,
        }
        img = Image.from_dict(data)
        assert img is not None
        assert img.browser_link == "https://img.example.com/x.png"
        assert img.width == 800
        assert img.height == 600

    def test_from_dict_without_dimensions(self):
        data = {"browserLink": "https://img.example.com/no-size.png"}
        img = Image.from_dict(data)
        assert img is not None
        assert img.width is None
        assert img.height is None

    def test_from_dict_none_returns_none(self):
        assert Image.from_dict(None) is None

    def test_from_dict_maps_browser_link(self):
        data = {"browserLink": "https://coda.io/img/a.png"}
        img = Image.from_dict(data)
        assert img is not None
        assert img.browser_link == "https://coda.io/img/a.png"


# ---------------------------------------------------------------------------
# WorkspaceReference
# ---------------------------------------------------------------------------


class TestWorkspaceReference:
    def test_direct_construction(self):
        ws = WorkspaceReference(id="ws-123", name="My Workspace")
        assert ws.id == "ws-123"
        assert ws.type == "workspace"
        assert ws.name == "My Workspace"

    def test_default_type(self):
        ws = WorkspaceReference(id="ws-abc")
        assert ws.type == "workspace"

    def test_from_dict_full(self):
        data = {
            "id": "ws-456",
            "type": "workspace",
            "name": "Test WS",
            "organizationId": "org-99",
            "browserLink": "https://coda.io/ws",
        }
        ws = WorkspaceReference.from_dict(data)
        assert ws is not None
        assert ws.id == "ws-456"
        assert ws.organization_id == "org-99"
        assert ws.browser_link == "https://coda.io/ws"

    def test_from_dict_maps_organization_id(self):
        data = {"id": "ws-1", "organizationId": "org-42"}
        ws = WorkspaceReference.from_dict(data)
        assert ws is not None
        assert ws.organization_id == "org-42"

    def test_from_dict_defaults_type(self):
        data = {"id": "ws-2"}
        ws = WorkspaceReference.from_dict(data)
        assert ws is not None
        assert ws.type == "workspace"

    def test_from_dict_none_returns_none(self):
        assert WorkspaceReference.from_dict(None) is None


# ---------------------------------------------------------------------------
# FolderReference
# ---------------------------------------------------------------------------


class TestFolderReference:
    def test_direct_construction(self):
        f = FolderReference(id="fld-1")
        assert f.type == "folder"
        assert f.name is None

    def test_from_dict_full(self):
        data = {"id": "fld-2", "name": "My Folder", "browserLink": "https://coda.io/f"}
        f = FolderReference.from_dict(data)
        assert f is not None
        assert f.id == "fld-2"
        assert f.name == "My Folder"
        assert f.browser_link == "https://coda.io/f"

    def test_from_dict_defaults_type(self):
        data = {"id": "fld-3"}
        f = FolderReference.from_dict(data)
        assert f is not None
        assert f.type == "folder"

    def test_from_dict_none_returns_none(self):
        assert FolderReference.from_dict(None) is None


# ---------------------------------------------------------------------------
# DocSize
# ---------------------------------------------------------------------------


class TestDocSize:
    def test_direct_construction_defaults(self):
        ds = DocSize()
        assert ds.total_row_count == 0
        assert ds.table_and_view_count == 0
        assert ds.page_count == 0
        assert ds.over_api_size_limit is False

    def test_from_dict_all_fields(self):
        data = {
            "totalRowCount": 1500,
            "tableAndViewCount": 12,
            "pageCount": 45,
            "overApiSizeLimit": True,
        }
        ds = DocSize.from_dict(data)
        assert ds is not None
        assert ds.total_row_count == 1500
        assert ds.table_and_view_count == 12
        assert ds.page_count == 45
        assert ds.over_api_size_limit is True

    def test_from_dict_maps_over_api_size_limit(self):
        data = {"overApiSizeLimit": True}
        ds = DocSize.from_dict(data)
        assert ds is not None
        assert ds.over_api_size_limit is True

    def test_from_dict_missing_keys_use_defaults(self):
        ds = DocSize.from_dict({"totalRowCount": 10})
        assert ds is not None
        assert ds.table_and_view_count == 0
        assert ds.page_count == 0
        assert ds.over_api_size_limit is False

    def test_from_dict_none_returns_none(self):
        assert DocSize.from_dict(None) is None


# ---------------------------------------------------------------------------
# PageReference
# ---------------------------------------------------------------------------


class TestPageReference:
    def test_direct_construction(self):
        p = PageReference(id="page-1", name="Dashboard")
        assert p.type == "page"

    def test_from_dict_full(self):
        data = {
            "id": "page-2",
            "name": "Home",
            "href": "/docs/d1/pages/page-2",
            "browserLink": "https://coda.io/d/d1/page-2",
        }
        p = PageReference.from_dict(data)
        assert p is not None
        assert p.id == "page-2"
        assert p.name == "Home"
        assert p.href == "/docs/d1/pages/page-2"
        assert p.browser_link == "https://coda.io/d/d1/page-2"

    def test_from_dict_maps_href(self):
        data = {"id": "page-3", "href": "/api/pages/page-3"}
        p = PageReference.from_dict(data)
        assert p is not None
        assert p.href == "/api/pages/page-3"

    def test_from_dict_defaults_type(self):
        data = {"id": "page-4"}
        p = PageReference.from_dict(data)
        assert p is not None
        assert p.type == "page"

    def test_from_dict_none_returns_none(self):
        assert PageReference.from_dict(None) is None


# ---------------------------------------------------------------------------
# TableReference
# ---------------------------------------------------------------------------


class TestTableReference:
    def test_direct_construction(self):
        t = TableReference(id="tbl-1")
        assert t.type == "table"
        assert t.table_type is None

    def test_from_dict_full(self):
        data = {
            "id": "tbl-2",
            "name": "Users",
            "tableType": "table",
            "href": "/tables/tbl-2",
            "browserLink": "https://coda.io/t/tbl-2",
        }
        t = TableReference.from_dict(data)
        assert t is not None
        assert t.id == "tbl-2"
        assert t.name == "Users"
        assert t.table_type == "table"
        assert t.href == "/tables/tbl-2"

    def test_from_dict_maps_table_type(self):
        data = {"id": "tbl-3", "tableType": "view"}
        t = TableReference.from_dict(data)
        assert t is not None
        assert t.table_type == "view"

    def test_from_dict_none_returns_none(self):
        assert TableReference.from_dict(None) is None


# ---------------------------------------------------------------------------
# ColumnReference
# ---------------------------------------------------------------------------


class TestColumnReference:
    def test_direct_construction(self):
        c = ColumnReference(id="col-1")
        assert c.type == "column"
        assert c.href is None

    def test_from_dict_full(self):
        data = {"id": "col-2", "href": "/tables/t1/columns/col-2"}
        c = ColumnReference.from_dict(data)
        assert c is not None
        assert c.id == "col-2"
        assert c.href == "/tables/t1/columns/col-2"

    def test_from_dict_defaults_type(self):
        data = {"id": "col-3"}
        c = ColumnReference.from_dict(data)
        assert c is not None
        assert c.type == "column"

    def test_from_dict_none_returns_none(self):
        assert ColumnReference.from_dict(None) is None


# ---------------------------------------------------------------------------
# PersonValue
# ---------------------------------------------------------------------------


class TestPersonValue:
    def test_direct_construction(self):
        p = PersonValue(name="Alice", email="alice@example.com")
        assert p.name == "Alice"
        assert p.email == "alice@example.com"

    def test_defaults_all_none(self):
        p = PersonValue()
        assert p.name is None
        assert p.email is None

    def test_from_dict_full(self):
        data = {"name": "Bob", "email": "bob@example.com"}
        p = PersonValue.from_dict(data)
        assert p is not None
        assert p.name == "Bob"
        assert p.email == "bob@example.com"

    def test_from_dict_partial(self):
        data = {"name": "Charlie"}
        p = PersonValue.from_dict(data)
        assert p is not None
        assert p.name == "Charlie"
        assert p.email is None

    def test_from_dict_none_returns_none(self):
        assert PersonValue.from_dict(None) is None

    def test_from_dict_empty_dict_returns_none(self):
        assert PersonValue.from_dict({}) is None


# ---------------------------------------------------------------------------
# Doc
# ---------------------------------------------------------------------------


class TestDoc:
    def _minimal_dict(self):
        return {
            "id": "AbCd1234",
            "type": "doc",
            "href": "/docs/AbCd1234",
            "browserLink": "https://coda.io/d/My-Doc_AbCd1234",
            "name": "My Doc",
            "owner": "owner@example.com",
            "ownerName": "Jane Doe",
        }

    def test_from_dict_minimal_required_fields(self):
        doc = Doc.from_dict(self._minimal_dict())
        assert doc.id == "AbCd1234"
        assert doc.type == "doc"
        assert doc.href == "/docs/AbCd1234"
        assert doc.name == "My Doc"
        assert doc.owner == "owner@example.com"

    def test_from_dict_maps_browser_link(self):
        doc = Doc.from_dict(self._minimal_dict())
        assert doc.browser_link == "https://coda.io/d/My-Doc_AbCd1234"

    def test_from_dict_maps_owner_name(self):
        doc = Doc.from_dict(self._minimal_dict())
        assert doc.owner_name == "Jane Doe"

    def test_from_dict_optional_fields_default_none(self):
        doc = Doc.from_dict(self._minimal_dict())
        assert doc.workspace is None
        assert doc.folder is None
        assert doc.icon is None
        assert doc.doc_size is None
        assert doc.created_at is None
        assert doc.updated_at is None

    def test_from_dict_nested_workspace(self):
        data = dict(self._minimal_dict())
        data["workspace"] = {"id": "ws-1", "name": "My WS"}
        doc = Doc.from_dict(data)
        assert doc.workspace is not None
        assert isinstance(doc.workspace, WorkspaceReference)
        assert doc.workspace.id == "ws-1"

    def test_from_dict_nested_folder(self):
        data = dict(self._minimal_dict())
        data["folder"] = {"id": "fld-1", "name": "Projects"}
        doc = Doc.from_dict(data)
        assert doc.folder is not None
        assert isinstance(doc.folder, FolderReference)
        assert doc.folder.name == "Projects"

    def test_from_dict_nested_icon(self):
        data = dict(self._minimal_dict())
        data["icon"] = {"name": "rocket", "type": "emoji"}
        doc = Doc.from_dict(data)
        assert doc.icon is not None
        assert isinstance(doc.icon, Icon)
        assert doc.icon.name == "rocket"

    def test_from_dict_nested_doc_size(self):
        data = dict(self._minimal_dict())
        data["docSize"] = {
            "totalRowCount": 200,
            "tableAndViewCount": 3,
            "pageCount": 10,
        }
        doc = Doc.from_dict(data)
        assert doc.doc_size is not None
        assert isinstance(doc.doc_size, DocSize)
        assert doc.doc_size.total_row_count == 200

    def test_from_dict_datetime_iso8601_z_suffix(self):
        data = dict(self._minimal_dict())
        data["createdAt"] = "2024-01-15T10:30:00Z"
        data["updatedAt"] = "2024-06-20T14:00:00Z"
        doc = Doc.from_dict(data)
        assert doc.created_at is not None
        assert doc.updated_at is not None
        assert doc.created_at.year == 2024
        assert doc.created_at.month == 1
        assert doc.updated_at.month == 6

    def test_from_dict_deprecated_workspace_id(self):
        data = dict(self._minimal_dict())
        data["workspaceId"] = "ws-deprecated"
        data["folderId"] = "fld-deprecated"
        doc = Doc.from_dict(data)
        assert doc.workspace_id == "ws-deprecated"
        assert doc.folder_id == "fld-deprecated"


# ---------------------------------------------------------------------------
# DocList
# ---------------------------------------------------------------------------


class TestDocList:
    def _minimal_doc_dict(self, doc_id="d1"):
        return {
            "id": doc_id,
            "type": "doc",
            "href": f"/docs/{doc_id}",
            "browserLink": f"https://coda.io/d/{doc_id}",
            "name": "Doc",
            "owner": "owner@example.com",
            "ownerName": "Owner",
        }

    def test_from_dict_empty_items(self):
        dl = DocList.from_dict({"items": []})
        assert dl.items == []
        assert dl.next_page_token is None

    def test_from_dict_with_one_doc(self):
        data = {"items": [self._minimal_doc_dict("d1")]}
        dl = DocList.from_dict(data)
        assert len(dl.items) == 1
        assert isinstance(dl.items[0], Doc)
        assert dl.items[0].id == "d1"

    def test_from_dict_with_multiple_docs(self):
        data = {"items": [self._minimal_doc_dict("d1"), self._minimal_doc_dict("d2")]}
        dl = DocList.from_dict(data)
        assert len(dl.items) == 2
        assert dl.items[1].id == "d2"

    def test_from_dict_pagination_fields(self):
        data = {
            "items": [],
            "href": "/docs?limit=10",
            "nextPageToken": "tok123",
            "nextPageLink": "/docs?pageToken=tok123",
        }
        dl = DocList.from_dict(data)
        assert dl.href == "/docs?limit=10"
        assert dl.next_page_token == "tok123"
        assert dl.next_page_link == "/docs?pageToken=tok123"

    def test_from_dict_missing_items_key(self):
        dl = DocList.from_dict({})
        assert dl.items == []


# ---------------------------------------------------------------------------
# Page
# ---------------------------------------------------------------------------


class TestPage:
    def _minimal_page_dict(self):
        return {
            "id": "pg-1",
            "type": "page",
            "href": "/pages/pg-1",
            "name": "Home",
            "isHidden": False,
            "isEffectivelyHidden": False,
            "browserLink": "https://coda.io/p/pg-1",
            "children": [],
            "contentType": "canvas",
        }

    def test_from_dict_minimal(self):
        page = Page.from_dict(self._minimal_page_dict())
        assert page.id == "pg-1"
        assert page.name == "Home"
        assert page.is_hidden is False
        assert page.is_effectively_hidden is False
        assert page.children == []

    def test_from_dict_maps_is_hidden(self):
        data = dict(self._minimal_page_dict())
        data["isHidden"] = True
        page = Page.from_dict(data)
        assert page.is_hidden is True

    def test_from_dict_with_icon(self):
        data = dict(self._minimal_page_dict())
        data["icon"] = {"name": "house", "type": "emoji"}
        page = Page.from_dict(data)
        assert page.icon is not None
        assert page.icon.name == "house"

    def test_from_dict_with_image(self):
        data = dict(self._minimal_page_dict())
        data["image"] = {"browserLink": "https://img.coda.io/cover.png", "width": 1200}
        page = Page.from_dict(data)
        assert page.image is not None
        assert page.image.width == 1200

    def test_from_dict_with_children(self):
        data = dict(self._minimal_page_dict())
        data["children"] = [
            {"id": "pg-2", "name": "Sub", "type": "page", "href": "/pages/pg-2"}
        ]
        page = Page.from_dict(data)
        assert len(page.children) == 1
        assert isinstance(page.children[0], PageReference)
        assert page.children[0].id == "pg-2"

    def test_from_dict_with_authors(self):
        data = dict(self._minimal_page_dict())
        data["authors"] = [{"name": "Alice", "email": "alice@example.com"}]
        page = Page.from_dict(data)
        assert page.authors is not None
        assert len(page.authors) == 1
        assert page.authors[0].name == "Alice"

    def test_from_dict_authors_none_when_missing(self):
        page = Page.from_dict(self._minimal_page_dict())
        assert page.authors is None

    def test_from_dict_with_parent(self):
        data = dict(self._minimal_page_dict())
        data["parent"] = {"id": "pg-root", "type": "page", "href": "/pages/pg-root"}
        page = Page.from_dict(data)
        assert page.parent is not None
        assert page.parent.id == "pg-root"

    def test_from_dict_datetime_parsing(self):
        data = dict(self._minimal_page_dict())
        data["createdAt"] = "2023-05-01T09:00:00Z"
        page = Page.from_dict(data)
        assert page.created_at is not None
        assert page.created_at.year == 2023


# ---------------------------------------------------------------------------
# PageList
# ---------------------------------------------------------------------------


class TestPageList:
    def test_from_dict_empty(self):
        pl = PageList.from_dict({"items": []})
        assert pl.items == []

    def test_from_dict_pagination(self):
        pl = PageList.from_dict({"items": [], "nextPageToken": "pt1"})
        assert pl.next_page_token == "pt1"


# ---------------------------------------------------------------------------
# PageContentItem
# ---------------------------------------------------------------------------


class TestPageContentItem:
    def test_from_dict_basic(self):
        item = PageContentItem.from_dict(
            {"id": "ci-1", "type": "paragraph", "text": "Hello"}
        )
        assert item.id == "ci-1"
        assert item.type == "paragraph"
        assert item.text == "Hello"

    def test_from_dict_no_text(self):
        item = PageContentItem.from_dict({"id": "ci-2", "type": "image"})
        assert item.text is None


# ---------------------------------------------------------------------------
# Sort
# ---------------------------------------------------------------------------


class TestSort:
    def test_from_dict_with_column(self):
        data = {
            "column": {"id": "col-1", "href": "/columns/col-1"},
            "direction": "ascending",
        }
        s = Sort.from_dict(data)
        assert s.direction == "ascending"
        assert isinstance(s.column, ColumnReference)
        assert s.column.id == "col-1"

    def test_from_dict_missing_column_uses_empty_fallback(self):
        data = {"direction": "descending"}
        s = Sort.from_dict(data)
        assert s.column.id == ""
        assert s.direction == "descending"

    def test_from_dict_default_direction(self):
        data = {"column": {"id": "col-2"}}
        s = Sort.from_dict(data)
        assert s.direction == "ascending"


# ---------------------------------------------------------------------------
# Table
# ---------------------------------------------------------------------------


class TestTable:
    def _minimal_table_dict(self):
        return {
            "id": "tbl-10",
            "type": "table",
            "tableType": "table",
            "href": "/tables/tbl-10",
            "name": "Projects",
            "browserLink": "https://coda.io/t/tbl-10",
            "rowCount": 42,
            "layout": "default",
        }

    def test_from_dict_minimal(self):
        tbl = Table.from_dict(self._minimal_table_dict())
        assert tbl.id == "tbl-10"
        assert tbl.row_count == 42
        assert tbl.layout == "default"
        assert tbl.sorts is None

    def test_from_dict_with_sorts(self):
        data = dict(self._minimal_table_dict())
        data["sorts"] = [{"column": {"id": "col-1"}, "direction": "descending"}]
        tbl = Table.from_dict(data)
        assert tbl.sorts is not None
        assert len(tbl.sorts) == 1
        assert tbl.sorts[0].direction == "descending"

    def test_from_dict_with_parent(self):
        data = dict(self._minimal_table_dict())
        data["parent"] = {"id": "pg-1", "type": "page", "href": "/pages/pg-1"}
        tbl = Table.from_dict(data)
        assert tbl.parent is not None
        assert tbl.parent.id == "pg-1"

    def test_from_dict_datetime(self):
        data = dict(self._minimal_table_dict())
        data["createdAt"] = "2024-03-01T00:00:00Z"
        tbl = Table.from_dict(data)
        assert tbl.created_at is not None
        assert tbl.created_at.year == 2024


# ---------------------------------------------------------------------------
# TableList
# ---------------------------------------------------------------------------


class TestTableList:
    def test_from_dict_empty(self):
        tl = TableList.from_dict({"items": []})
        assert tl.items == []

    def test_from_dict_pagination(self):
        tl = TableList.from_dict({"items": [], "nextPageToken": "tp1"})
        assert tl.next_page_token == "tp1"


# ---------------------------------------------------------------------------
# Column
# ---------------------------------------------------------------------------


class TestColumn:
    def test_from_dict_basic(self):
        data = {
            "id": "col-10",
            "type": "column",
            "href": "/columns/col-10",
            "name": "Status",
            "format": {"type": "text"},
        }
        col = Column.from_dict(data)
        assert col.id == "col-10"
        assert col.name == "Status"
        assert col.format == {"type": "text"}
        assert col.display is False
        assert col.calculated is False

    def test_from_dict_calculated_column(self):
        data = {
            "id": "col-11",
            "type": "column",
            "href": "/columns/col-11",
            "name": "Full Name",
            "format": {},
            "calculated": True,
            "formula": "Concatenate(First, ' ', Last)",
        }
        col = Column.from_dict(data)
        assert col.calculated is True
        assert col.formula == "Concatenate(First, ' ', Last)"

    def test_from_dict_default_format(self):
        data = {"id": "col-12", "type": "column", "href": "/c/col-12", "name": "X"}
        col = Column.from_dict(data)
        assert col.format == {}


# ---------------------------------------------------------------------------
# ColumnList
# ---------------------------------------------------------------------------


class TestColumnList:
    def test_from_dict_empty(self):
        cl = ColumnList.from_dict({"items": []})
        assert cl.items == []


# ---------------------------------------------------------------------------
# Row
# ---------------------------------------------------------------------------


class TestRow:
    def test_from_dict_basic(self):
        data = {
            "id": "row-1",
            "type": "row",
            "href": "/rows/row-1",
            "name": "Row 1",
            "index": 0,
            "browserLink": "https://coda.io/r/row-1",
            "values": {"col-a": "hello", "col-b": 42},
        }
        row = Row.from_dict(data)
        assert row.id == "row-1"
        assert row.index == 0
        assert row.values["col-a"] == "hello"
        assert row.values["col-b"] == 42

    def test_from_dict_default_values(self):
        data = {
            "id": "row-2",
            "type": "row",
            "href": "/r/row-2",
            "name": "R",
            "index": 1,
            "browserLink": "",
        }
        row = Row.from_dict(data)
        assert row.values == {}

    def test_from_dict_datetime(self):
        data = {
            "id": "row-3",
            "type": "row",
            "href": "/r/row-3",
            "name": "R",
            "index": 2,
            "browserLink": "",
            "createdAt": "2024-01-01T00:00:00Z",
        }
        row = Row.from_dict(data)
        assert row.created_at is not None
        assert row.created_at.year == 2024


# ---------------------------------------------------------------------------
# RowList
# ---------------------------------------------------------------------------


class TestRowList:
    def test_from_dict_empty(self):
        rl = RowList.from_dict({"items": []})
        assert rl.items == []

    def test_from_dict_next_sync_token(self):
        rl = RowList.from_dict({"items": [], "nextSyncToken": "sync-abc"})
        assert rl.next_sync_token == "sync-abc"


# ---------------------------------------------------------------------------
# CellEdit and RowEdit — to_dict
# ---------------------------------------------------------------------------


class TestCellEdit:
    def test_to_dict(self):
        cell = CellEdit(column="col-1", value="hello")
        d = cell.to_dict()
        assert d == {"column": "col-1", "value": "hello"}

    def test_to_dict_none_value(self):
        cell = CellEdit(column="col-2", value=None)
        d = cell.to_dict()
        assert d["value"] is None

    def test_to_dict_numeric_value(self):
        cell = CellEdit(column="col-3", value=99)
        assert cell.to_dict()["value"] == 99


class TestRowEdit:
    def test_to_dict_single_cell(self):
        row = RowEdit(cells=[CellEdit(column="col-1", value="x")])
        d = row.to_dict()
        assert "cells" in d
        assert len(d["cells"]) == 1
        assert d["cells"][0] == {"column": "col-1", "value": "x"}

    def test_to_dict_multiple_cells(self):
        row = RowEdit(cells=[CellEdit("c1", "a"), CellEdit("c2", "b")])
        d = row.to_dict()
        assert len(d["cells"]) == 2

    def test_to_dict_empty_cells(self):
        row = RowEdit(cells=[])
        assert row.to_dict() == {"cells": []}


# ---------------------------------------------------------------------------
# Formula
# ---------------------------------------------------------------------------


class TestFormula:
    def test_from_dict_basic(self):
        data = {
            "id": "f-1",
            "type": "formula",
            "href": "/formulas/f-1",
            "name": "Total",
            "value": 42,
        }
        f = Formula.from_dict(data)
        assert f.id == "f-1"
        assert f.name == "Total"
        assert f.value == 42
        assert f.parent is None

    def test_from_dict_with_parent(self):
        data = {
            "id": "f-2",
            "type": "formula",
            "href": "/f/f-2",
            "name": "Avg",
            "value": 10.5,
            "parent": {"id": "pg-1", "type": "page", "href": "/pages/pg-1"},
        }
        f = Formula.from_dict(data)
        assert f.parent is not None
        assert f.parent.id == "pg-1"


# ---------------------------------------------------------------------------
# FormulaList
# ---------------------------------------------------------------------------


class TestFormulaList:
    def test_from_dict_empty(self):
        fl = FormulaList.from_dict({"items": []})
        assert fl.items == []


# ---------------------------------------------------------------------------
# Control
# ---------------------------------------------------------------------------


class TestControl:
    def test_from_dict_basic(self):
        data = {
            "id": "ctrl-1",
            "type": "control",
            "href": "/controls/ctrl-1",
            "name": "Slider",
            "controlType": "slider",
            "value": 50,
        }
        ctrl = Control.from_dict(data)
        assert ctrl.id == "ctrl-1"
        assert ctrl.control_type == "slider"
        assert ctrl.value == 50

    def test_from_dict_button_type(self):
        data = {
            "id": "ctrl-2",
            "type": "control",
            "href": "/c/ctrl-2",
            "name": "Submit",
            "controlType": "button",
            "value": None,
        }
        ctrl = Control.from_dict(data)
        assert ctrl.control_type == "button"


# ---------------------------------------------------------------------------
# ControlList
# ---------------------------------------------------------------------------


class TestControlList:
    def test_from_dict_empty(self):
        cl = ControlList.from_dict({"items": []})
        assert cl.items == []


# ---------------------------------------------------------------------------
# Principal and Permission
# ---------------------------------------------------------------------------


class TestPrincipal:
    def test_from_dict_email_type(self):
        p = Principal.from_dict({"type": "email", "email": "alice@example.com"})
        assert p.type == "email"
        assert p.email == "alice@example.com"

    def test_from_dict_anyone_type(self):
        p = Principal.from_dict({"type": "anyone"})
        assert p.type == "anyone"
        assert p.email is None

    def test_to_dict_with_email(self):
        p = Principal(type="email", email="bob@example.com")
        d = p.to_dict()
        assert d == {"type": "email", "email": "bob@example.com"}

    def test_to_dict_without_email(self):
        p = Principal(type="domain")
        d = p.to_dict()
        assert d == {"type": "domain"}
        assert "email" not in d


class TestPermission:
    def test_from_dict(self):
        data = {
            "id": "perm-1",
            "principal": {"type": "email", "email": "user@example.com"},
            "access": "readonly",
        }
        perm = Permission.from_dict(data)
        assert perm.id == "perm-1"
        assert perm.access == "readonly"
        assert isinstance(perm.principal, Principal)
        assert perm.principal.email == "user@example.com"


# ---------------------------------------------------------------------------
# PermissionList
# ---------------------------------------------------------------------------


class TestPermissionList:
    def test_from_dict_empty(self):
        pl = PermissionList.from_dict({"items": [], "href": "/perms"})
        assert pl.items == []
        assert pl.href == "/perms"


# ---------------------------------------------------------------------------
# SharingMetadata
# ---------------------------------------------------------------------------


class TestSharingMetadata:
    def test_from_dict_all_true(self):
        data = {
            "canShare": True,
            "canShareWithWorkspace": True,
            "canShareWithOrg": True,
            "canCopy": True,
        }
        sm = SharingMetadata.from_dict(data)
        assert sm.can_share is True
        assert sm.can_share_with_workspace is True
        assert sm.can_share_with_org is True
        assert sm.can_copy is True

    def test_from_dict_defaults_false(self):
        sm = SharingMetadata.from_dict({})
        assert sm.can_share is False
        assert sm.can_copy is False


# ---------------------------------------------------------------------------
# ACLSettings
# ---------------------------------------------------------------------------


class TestACLSettings:
    def test_from_dict_all_true(self):
        data = {
            "allowEditorsToChangePermissions": True,
            "allowCopying": True,
            "allowViewersToRequestEditing": True,
        }
        acl = ACLSettings.from_dict(data)
        assert acl.allow_editors_to_change_permissions is True
        assert acl.allow_copying is True
        assert acl.allow_viewers_to_request_editing is True

    def test_from_dict_defaults_false(self):
        acl = ACLSettings.from_dict({})
        assert acl.allow_editors_to_change_permissions is False
        assert acl.allow_copying is False


# ---------------------------------------------------------------------------
# User
# ---------------------------------------------------------------------------


class TestUser:
    def test_from_dict_basic(self):
        data = {
            "name": "Alice",
            "loginId": "alice@example.com",
            "type": "user",
            "scoped": False,
            "tokenName": "My Token",
            "href": "/whoami",
        }
        user = User.from_dict(data)
        assert user.name == "Alice"
        assert user.login_id == "alice@example.com"
        assert user.scoped is False
        assert user.token_name == "My Token"
        assert user.workspace is None

    def test_from_dict_maps_login_id(self):
        data = {
            "name": "Bob",
            "loginId": "bob@example.com",
            "type": "user",
            "scoped": True,
            "tokenName": "t",
            "href": "/",
        }
        user = User.from_dict(data)
        assert user.login_id == "bob@example.com"

    def test_from_dict_with_workspace(self):
        data = {
            "name": "Carol",
            "loginId": "carol@example.com",
            "type": "user",
            "scoped": False,
            "tokenName": "tok",
            "href": "/whoami",
            "workspace": {"id": "ws-1", "name": "Carol's WS"},
        }
        user = User.from_dict(data)
        assert user.workspace is not None
        assert user.workspace.id == "ws-1"


# ---------------------------------------------------------------------------
# MutationStatus
# ---------------------------------------------------------------------------


class TestMutationStatus:
    def test_from_dict_completed(self):
        ms = MutationStatus.from_dict({"completed": True})
        assert ms.completed is True
        assert ms.warning is None

    def test_from_dict_not_completed(self):
        ms = MutationStatus.from_dict({"completed": False})
        assert ms.completed is False

    def test_from_dict_with_warning(self):
        ms = MutationStatus.from_dict({"completed": True, "warning": "Rate limit near"})
        assert ms.warning == "Rate limit near"

    def test_from_dict_default_not_completed(self):
        ms = MutationStatus.from_dict({})
        assert ms.completed is False


# ---------------------------------------------------------------------------
# InsertRowsResult
# ---------------------------------------------------------------------------


class TestInsertRowsResult:
    def test_from_dict_with_row_ids(self):
        data = {"requestId": "req-abc", "addedRowIds": ["row-1", "row-2"]}
        result = InsertRowsResult.from_dict(data)
        assert result.request_id == "req-abc"
        assert result.added_row_ids == ["row-1", "row-2"]

    def test_from_dict_without_row_ids(self):
        result = InsertRowsResult.from_dict({"requestId": "req-xyz"})
        assert result.added_row_ids is None

    def test_from_dict_empty_dict(self):
        result = InsertRowsResult.from_dict({})
        assert result.request_id == ""
        assert result.added_row_ids is None


# ---------------------------------------------------------------------------
# _parse_datetime helper (tested indirectly via Doc)
# ---------------------------------------------------------------------------


class TestParseDatetimeViaDoc:
    def _doc_base(self):
        return {
            "id": "d1",
            "type": "doc",
            "href": "/d/d1",
            "browserLink": "https://coda.io/d/d1",
            "name": "D",
            "owner": "o@x.com",
            "ownerName": "O",
        }

    def test_parse_z_suffix_datetime(self):
        data = dict(self._doc_base())
        data["createdAt"] = "2024-12-31T23:59:59Z"
        doc = Doc.from_dict(data)
        assert doc.created_at is not None
        assert doc.created_at.day == 31
        assert doc.created_at.month == 12

    def test_parse_offset_datetime(self):
        data = dict(self._doc_base())
        data["createdAt"] = "2024-06-15T12:00:00+05:30"
        doc = Doc.from_dict(data)
        assert doc.created_at is not None
        assert doc.created_at.year == 2024

    def test_invalid_datetime_yields_none(self):
        data = dict(self._doc_base())
        data["createdAt"] = "not-a-date"
        doc = Doc.from_dict(data)
        assert doc.created_at is None

    def test_none_datetime_yields_none(self):
        doc = Doc.from_dict(self._doc_base())
        assert doc.created_at is None
