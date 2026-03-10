"""Comprehensive tests for cloud.coda_io.models — zero-mock.

Covers enums (TableType, PageType, ControlType, AccessType, DocPublishMode, ValueFormat),
reference types (Icon, Image, WorkspaceReference, FolderReference, DocSize, PageReference,
TableReference, ColumnReference), and from_dict deserialization.
"""


from codomyrmex.cloud.coda_io.models import (
    AccessType,
    ColumnReference,
    ControlType,
    DocPublishMode,
    DocSize,
    FolderReference,
    Icon,
    Image,
    PageReference,
    PageType,
    TableReference,
    TableType,
    ValueFormat,
    WorkspaceReference,
)

# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class TestEnums:
    def test_table_type(self):
        assert TableType.TABLE.value == "table"
        assert TableType.VIEW.value == "view"

    def test_page_type(self):
        assert PageType.CANVAS.value == "canvas"
        assert PageType.EMBED.value == "embed"
        assert PageType.SYNC_PAGE.value == "syncPage"

    def test_control_type_values(self):
        assert ControlType.BUTTON.value == "button"
        assert ControlType.CHECKBOX.value == "checkbox"
        assert ControlType.SELECT.value == "select"
        assert ControlType.SLIDER.value == "slider"
        assert ControlType.TEXTBOX.value == "textbox"

    def test_access_type(self):
        assert AccessType.NONE.value == "none"
        assert AccessType.READONLY.value == "readonly"
        assert AccessType.WRITE.value == "write"

    def test_doc_publish_mode(self):
        assert DocPublishMode.VIEW.value == "view"
        assert DocPublishMode.PLAY.value == "play"
        assert DocPublishMode.EDIT.value == "edit"

    def test_value_format(self):
        assert ValueFormat.SIMPLE.value == "simple"
        assert ValueFormat.RICH.value == "rich"


# ---------------------------------------------------------------------------
# Icon
# ---------------------------------------------------------------------------


class TestIcon:
    def test_create_icon(self):
        icon = Icon(name="star", type="emoji")
        assert icon.name == "star"

    def test_from_dict(self):
        data = {"name": "folder", "type": "system", "browserLink": "https://example.com"}
        icon = Icon.from_dict(data)
        assert icon is not None
        assert icon.name == "folder"

    def test_from_dict_none(self):
        result = Icon.from_dict(None)
        assert result is None


# ---------------------------------------------------------------------------
# Image
# ---------------------------------------------------------------------------


class TestImage:
    def test_create_image(self):
        img = Image(browser_link="https://img.example.com/photo.jpg")
        assert img.browser_link is not None

    def test_from_dict(self):
        data = {"browserLink": "https://img.example.com/x.png", "width": 800, "height": 600}
        img = Image.from_dict(data)
        assert img is not None
        assert img.width == 800

    def test_from_dict_none(self):
        result = Image.from_dict(None)
        assert result is None


# ---------------------------------------------------------------------------
# WorkspaceReference
# ---------------------------------------------------------------------------


class TestWorkspaceReference:
    def test_create(self):
        ws = WorkspaceReference(id="ws-123", name="My Workspace")
        assert ws.id == "ws-123"
        assert ws.type == "workspace"

    def test_from_dict(self):
        data = {"id": "ws-456", "name": "Test WS", "browserLink": "https://coda.io/ws"}
        ws = WorkspaceReference.from_dict(data)
        assert ws is not None
        assert ws.id == "ws-456"

    def test_from_dict_none(self):
        result = WorkspaceReference.from_dict(None)
        assert result is None


# ---------------------------------------------------------------------------
# FolderReference
# ---------------------------------------------------------------------------


class TestFolderReference:
    def test_create(self):
        f = FolderReference(id="fld-1")
        assert f.type == "folder"

    def test_from_dict(self):
        data = {"id": "fld-2", "name": "My Folder"}
        f = FolderReference.from_dict(data)
        assert f is not None
        assert f.id == "fld-2"

    def test_from_dict_none(self):
        assert FolderReference.from_dict(None) is None


# ---------------------------------------------------------------------------
# DocSize
# ---------------------------------------------------------------------------


class TestDocSize:
    def test_create_defaults(self):
        ds = DocSize()
        assert ds.total_row_count == 0
        assert ds.over_api_size_limit is False

    def test_from_dict(self):
        data = {"totalRowCount": 100, "tableAndViewCount": 5, "pageCount": 3}
        ds = DocSize.from_dict(data)
        assert ds is not None
        assert ds.total_row_count == 100

    def test_from_dict_none(self):
        assert DocSize.from_dict(None) is None


# ---------------------------------------------------------------------------
# PageReference
# ---------------------------------------------------------------------------


class TestPageReference:
    def test_create(self):
        p = PageReference(id="page-1", name="Dashboard")
        assert p.type == "page"

    def test_from_dict(self):
        data = {"id": "page-2", "name": "Home", "browserLink": "https://coda.io/p"}
        p = PageReference.from_dict(data)
        assert p is not None
        assert p.name == "Home"

    def test_from_dict_none(self):
        assert PageReference.from_dict(None) is None


# ---------------------------------------------------------------------------
# TableReference
# ---------------------------------------------------------------------------


class TestTableReference:
    def test_create(self):
        t = TableReference(id="tbl-1")
        assert t.type == "table"

    def test_from_dict(self):
        data = {"id": "tbl-2", "name": "Users", "tableType": "table"}
        t = TableReference.from_dict(data)
        assert t is not None
        assert t.name == "Users"

    def test_from_dict_none(self):
        assert TableReference.from_dict(None) is None


# ---------------------------------------------------------------------------
# ColumnReference
# ---------------------------------------------------------------------------


class TestColumnReference:
    def test_create(self):
        c = ColumnReference(id="col-1")
        assert c.type == "column"

    def test_from_dict(self):
        data = {"id": "col-2", "href": "/tables/t1/columns/col-2"}
        c = ColumnReference.from_dict(data)
        assert c is not None
        assert c.id == "col-2"

    def test_from_dict_none(self):
        assert ColumnReference.from_dict(None) is None
