# type: ignore
"""Deep execution-path tests for cloud/coda_io models — zero-mock.

Exercises data model deserialization (from_dict), enum values,
and reference type construction for the full Coda API model layer.
"""

from __future__ import annotations

import pytest

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
# Enum Tests
# ---------------------------------------------------------------------------


class TestCodaEnums:
    """All Coda enums have expected members."""

    def test_table_type(self) -> None:
        assert TableType.TABLE.value == "table"
        assert TableType.VIEW.value == "view"

    def test_page_type(self) -> None:
        assert PageType.CANVAS.value == "canvas"

    def test_control_type_members(self) -> None:
        assert len(list(ControlType)) >= 10

    def test_access_type(self) -> None:
        assert AccessType.READONLY.value == "readonly"

    def test_doc_publish_mode(self) -> None:
        assert DocPublishMode.VIEW.value == "view"

    def test_value_format(self) -> None:
        assert ValueFormat.SIMPLE.value == "simple"


# ---------------------------------------------------------------------------
# Reference Type Deserialization
# ---------------------------------------------------------------------------


class TestIconDeserialization:
    """Icon.from_dict round-trip."""

    def test_from_dict(self) -> None:
        icon = Icon.from_dict({"name": "star", "type": "emoji", "browserLink": "/icons/star"})
        assert icon is not None
        assert icon.name == "star"

    def test_from_none(self) -> None:
        result = Icon.from_dict(None)
        assert result is None or isinstance(result, Icon)


class TestImageDeserialization:
    """Image.from_dict round-trip."""

    def test_from_dict(self) -> None:
        img = Image.from_dict({"browserLink": "/img.png", "width": 100, "height": 50})
        assert img is not None
        assert img.width == 100

    def test_from_none(self) -> None:
        result = Image.from_dict(None)
        assert result is None or isinstance(result, Image)


class TestWorkspaceReference:
    """WorkspaceReference.from_dict."""

    def test_from_dict(self) -> None:
        ws = WorkspaceReference.from_dict({
            "id": "ws-1",
            "type": "workspace",
            "name": "My Workspace",
            "organizationId": "org-1",
        })
        assert ws is not None
        assert ws.id == "ws-1"

    def test_from_none(self) -> None:
        result = WorkspaceReference.from_dict(None)
        assert result is None or isinstance(result, WorkspaceReference)


class TestFolderReference:
    """FolderReference.from_dict."""

    def test_from_dict(self) -> None:
        f = FolderReference.from_dict({"id": "f-1", "name": "Folder A"})
        assert f is not None
        assert f.id == "f-1"


class TestDocSize:
    """DocSize.from_dict."""

    def test_from_dict(self) -> None:
        ds = DocSize.from_dict({"totalRowCount": 100, "tableAndViewCount": 5, "pageCount": 3})
        assert ds is not None
        assert ds.total_row_count == 100

    def test_from_none(self) -> None:
        result = DocSize.from_dict(None)
        assert result is None or isinstance(result, DocSize)


class TestPageReference:
    """PageReference.from_dict."""

    def test_from_dict(self) -> None:
        p = PageReference.from_dict({"id": "p-1", "name": "Page 1"})
        assert p is not None
        assert p.id == "p-1"


class TestTableReference:
    """TableReference.from_dict."""

    def test_from_dict(self) -> None:
        t = TableReference.from_dict({"id": "t-1", "tableType": "table", "name": "Users"})
        assert t is not None
        assert t.id == "t-1"


class TestColumnReference:
    """ColumnReference.from_dict."""

    def test_from_dict(self) -> None:
        c = ColumnReference.from_dict({"id": "col-1", "href": "/api/col/1"})
        assert c is not None
        assert c.id == "col-1"
