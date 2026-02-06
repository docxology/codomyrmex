"""
Unit tests for Coda.io API data models.

Tests serialization, deserialization, optional field handling,
and nested object parsing without requiring network access.
"""

from datetime import datetime

import pytest


@pytest.mark.unit
class TestDocModel:
    """Tests for the Doc dataclass model."""

    def test_doc_from_dict_minimal(self):
        """Test Doc creation with minimal required fields."""
        from codomyrmex.cloud.coda_io.models import Doc

        data = {
            "id": "AbCDeFGH",
            "type": "doc",
            "href": "https://coda.io/apis/v1/docs/AbCDeFGH",
            "browserLink": "https://coda.io/d/_dAbCDeFGH",
            "name": "Test Doc",
            "owner": "user@example.com",
            "ownerName": "Test User",
        }

        doc = Doc.from_dict(data)

        assert doc.id == "AbCDeFGH"
        assert doc.type == "doc"
        assert doc.href == "https://coda.io/apis/v1/docs/AbCDeFGH"
        assert doc.browser_link == "https://coda.io/d/_dAbCDeFGH"
        assert doc.name == "Test Doc"
        assert doc.owner == "user@example.com"
        assert doc.owner_name == "Test User"

    def test_doc_from_dict_with_timestamps(self):
        """Test Doc parses datetime fields correctly."""
        from codomyrmex.cloud.coda_io.models import Doc

        data = {
            "id": "AbCDeFGH",
            "type": "doc",
            "href": "https://coda.io/apis/v1/docs/AbCDeFGH",
            "browserLink": "https://coda.io/d/_dAbCDeFGH",
            "name": "Test Doc",
            "owner": "user@example.com",
            "ownerName": "Test User",
            "createdAt": "2024-01-15T10:30:00Z",
            "updatedAt": "2024-01-16T14:45:30Z",
        }

        doc = Doc.from_dict(data)

        assert doc.created_at is not None
        assert isinstance(doc.created_at, datetime)
        assert doc.updated_at is not None
        assert isinstance(doc.updated_at, datetime)

    def test_doc_from_dict_with_nested_objects(self):
        """Test Doc parses nested workspace and folder references."""
        from codomyrmex.cloud.coda_io.models import Doc

        data = {
            "id": "AbCDeFGH",
            "type": "doc",
            "href": "https://coda.io/apis/v1/docs/AbCDeFGH",
            "browserLink": "https://coda.io/d/_dAbCDeFGH",
            "name": "Test Doc",
            "owner": "user@example.com",
            "ownerName": "Test User",
            "workspace": {
                "id": "ws-1Ab234",
                "type": "workspace",
                "name": "My Workspace",
                "browserLink": "https://coda.io/docs?workspaceId=ws-1Ab234",
            },
            "folder": {
                "id": "fl-1Ab234",
                "type": "folder",
                "name": "My Folder",
                "browserLink": "https://coda.io/docs?folderId=fl-1Ab234",
            },
        }

        doc = Doc.from_dict(data)

        assert doc.workspace is not None
        assert doc.workspace.id == "ws-1Ab234"
        assert doc.workspace.name == "My Workspace"
        assert doc.folder is not None
        assert doc.folder.id == "fl-1Ab234"
        assert doc.folder.name == "My Folder"


@pytest.mark.unit
class TestDocListModel:
    """Tests for the DocList dataclass model."""

    def test_doclist_from_dict(self):
        """Test DocList parses list of docs."""
        from codomyrmex.cloud.coda_io.models import DocList

        data = {
            "items": [
                {
                    "id": "doc1",
                    "type": "doc",
                    "href": "https://coda.io/apis/v1/docs/doc1",
                    "browserLink": "https://coda.io/d/_ddoc1",
                    "name": "Doc 1",
                    "owner": "user@example.com",
                    "ownerName": "User",
                },
                {
                    "id": "doc2",
                    "type": "doc",
                    "href": "https://coda.io/apis/v1/docs/doc2",
                    "browserLink": "https://coda.io/d/_ddoc2",
                    "name": "Doc 2",
                    "owner": "user@example.com",
                    "ownerName": "User",
                },
            ],
            "href": "https://coda.io/apis/v1/docs?limit=20",
            "nextPageToken": "eyJsaW1pd",
            "nextPageLink": "https://coda.io/apis/v1/docs?pageToken=eyJsaW1pd",
        }

        doc_list = DocList.from_dict(data)

        assert len(doc_list.items) == 2
        assert doc_list.items[0].id == "doc1"
        assert doc_list.items[1].id == "doc2"
        assert doc_list.next_page_token == "eyJsaW1pd"
        assert doc_list.next_page_link is not None

    def test_doclist_empty(self):
        """Test DocList handles empty items list."""
        from codomyrmex.cloud.coda_io.models import DocList

        data = {"items": []}
        doc_list = DocList.from_dict(data)

        assert len(doc_list.items) == 0
        assert doc_list.next_page_token is None


@pytest.mark.unit
class TestPageModel:
    """Tests for the Page dataclass model."""

    def test_page_from_dict(self):
        """Test Page creation from API response."""
        from codomyrmex.cloud.coda_io.models import Page

        data = {
            "id": "canvas-IjkLmnO",
            "type": "page",
            "href": "https://coda.io/apis/v1/docs/AbCDeFGH/pages/canvas-IjkLmnO",
            "name": "Launch Status",
            "isHidden": False,
            "isEffectivelyHidden": False,
            "browserLink": "https://coda.io/d/_dAbCDeFGH/Launch-Status_sumnO",
            "children": [],
            "contentType": "canvas",
        }

        page = Page.from_dict(data)

        assert page.id == "canvas-IjkLmnO"
        assert page.name == "Launch Status"
        assert page.is_hidden is False
        assert page.content_type == "canvas"
        assert len(page.children) == 0

    def test_page_with_children(self):
        """Test Page with child page references."""
        from codomyrmex.cloud.coda_io.models import Page

        data = {
            "id": "canvas-parent",
            "type": "page",
            "href": "https://coda.io/apis/v1/docs/doc/pages/canvas-parent",
            "name": "Parent Page",
            "isHidden": False,
            "isEffectivelyHidden": False,
            "browserLink": "https://coda.io/d/_ddoc/Parent_s123",
            "contentType": "canvas",
            "children": [
                {
                    "id": "canvas-child1",
                    "type": "page",
                    "name": "Child 1",
                },
                {
                    "id": "canvas-child2",
                    "type": "page",
                    "name": "Child 2",
                },
            ],
        }

        page = Page.from_dict(data)

        assert len(page.children) == 2
        assert page.children[0].id == "canvas-child1"
        assert page.children[1].name == "Child 2"


@pytest.mark.unit
class TestTableModel:
    """Tests for the Table dataclass model."""

    def test_table_from_dict(self):
        """Test Table creation from API response."""
        from codomyrmex.cloud.coda_io.models import Table

        data = {
            "id": "grid-pqRst-U",
            "type": "table",
            "tableType": "table",
            "href": "https://coda.io/apis/v1/docs/AbCDeFGH/tables/grid-pqRst-U",
            "name": "Tasks",
            "browserLink": "https://coda.io/d/_dAbCDeFGH/#Teams-and-Tasks_tpqRst-U",
            "rowCount": 130,
            "layout": "default",
        }

        table = Table.from_dict(data)

        assert table.id == "grid-pqRst-U"
        assert table.table_type == "table"
        assert table.name == "Tasks"
        assert table.row_count == 130
        assert table.layout == "default"

    def test_table_view_type(self):
        """Test Table with view type."""
        from codomyrmex.cloud.coda_io.models import Table

        data = {
            "id": "table-view-123",
            "type": "table",
            "tableType": "view",
            "href": "https://coda.io/apis/v1/docs/doc/tables/table-view-123",
            "name": "Active Tasks View",
            "browserLink": "https://coda.io/d/_ddoc/#view_t123",
            "rowCount": 45,
            "layout": "card",
        }

        table = Table.from_dict(data)

        assert table.table_type == "view"
        assert table.layout == "card"


@pytest.mark.unit
class TestRowModel:
    """Tests for the Row dataclass model."""

    def test_row_from_dict(self):
        """Test Row creation from API response."""
        from codomyrmex.cloud.coda_io.models import Row

        data = {
            "id": "i-tuVwxYz",
            "type": "row",
            "href": "https://coda.io/apis/v1/docs/AbCDeFGH/tables/grid/rows/i-tuVwxYz",
            "name": "Apple",
            "index": 7,
            "browserLink": "https://coda.io/d/_dAbCDeFGH#_ri-tuVwxYz",
            "values": {
                "c-tuVwxYz": "Apple",
                "c-bCdeFgh": 42,
                "c-status": "Done",
            },
            "createdAt": "2024-01-15T10:30:00Z",
            "updatedAt": "2024-01-16T14:45:30Z",
        }

        row = Row.from_dict(data)

        assert row.id == "i-tuVwxYz"
        assert row.name == "Apple"
        assert row.index == 7
        assert row.values["c-tuVwxYz"] == "Apple"
        assert row.values["c-bCdeFgh"] == 42
        assert row.created_at is not None


@pytest.mark.unit
class TestColumnModel:
    """Tests for the Column dataclass model."""

    def test_column_from_dict(self):
        """Test Column creation from API response."""
        from codomyrmex.cloud.coda_io.models import Column

        data = {
            "id": "c-tuVwxYz",
            "type": "column",
            "href": "https://coda.io/apis/v1/docs/AbCDeFGH/tables/grid/columns/c-tuVwxYz",
            "name": "Status",
            "format": {"type": "select"},
            "display": False,
            "calculated": False,
        }

        column = Column.from_dict(data)

        assert column.id == "c-tuVwxYz"
        assert column.name == "Status"
        assert column.format == {"type": "select"}
        assert column.display is False
        assert column.calculated is False

    def test_column_with_formula(self):
        """Test Column with formula."""
        from codomyrmex.cloud.coda_io.models import Column

        data = {
            "id": "c-formula",
            "type": "column",
            "href": "https://coda.io/apis/v1/docs/doc/tables/table/columns/c-formula",
            "name": "Total",
            "format": {"type": "number"},
            "calculated": True,
            "formula": "thisRow.Price * thisRow.Quantity",
        }

        column = Column.from_dict(data)

        assert column.calculated is True
        assert column.formula == "thisRow.Price * thisRow.Quantity"


@pytest.mark.unit
class TestRowEditModel:
    """Tests for RowEdit and CellEdit models."""

    def test_cell_edit_to_dict(self):
        """Test CellEdit serialization."""
        from codomyrmex.cloud.coda_io.models import CellEdit

        cell = CellEdit(column="c-status", value="Done")
        result = cell.to_dict()

        assert result == {"column": "c-status", "value": "Done"}

    def test_row_edit_to_dict(self):
        """Test RowEdit serialization with multiple cells."""
        from codomyrmex.cloud.coda_io.models import CellEdit, RowEdit

        row = RowEdit(cells=[
            CellEdit(column="Task", value="New task"),
            CellEdit(column="Status", value="Todo"),
            CellEdit(column="Priority", value=1),
        ])

        result = row.to_dict()

        assert "cells" in result
        assert len(result["cells"]) == 3
        assert result["cells"][0] == {"column": "Task", "value": "New task"}


@pytest.mark.unit
class TestUserModel:
    """Tests for the User dataclass model."""

    def test_user_from_dict(self):
        """Test User creation from whoami response."""
        from codomyrmex.cloud.coda_io.models import User

        data = {
            "name": "John Doe",
            "loginId": "john@example.com",
            "type": "user",
            "scoped": False,
            "tokenName": "My API Token",
            "href": "https://coda.io/apis/v1/whoami",
            "workspace": {
                "id": "ws-123",
                "type": "workspace",
                "name": "My Workspace",
            },
            "pictureLink": "https://cdn.coda.io/avatars/default.png",
        }

        user = User.from_dict(data)

        assert user.name == "John Doe"
        assert user.login_id == "john@example.com"
        assert user.scoped is False
        assert user.token_name == "My API Token"
        assert user.workspace is not None
        assert user.workspace.id == "ws-123"


@pytest.mark.unit
class TestPermissionModels:
    """Tests for permission-related models."""

    def test_sharing_metadata_from_dict(self):
        """Test SharingMetadata creation."""
        from codomyrmex.cloud.coda_io.models import SharingMetadata

        data = {
            "canShare": True,
            "canShareWithWorkspace": True,
            "canShareWithOrg": False,
            "canCopy": True,
        }

        metadata = SharingMetadata.from_dict(data)

        assert metadata.can_share is True
        assert metadata.can_share_with_workspace is True
        assert metadata.can_share_with_org is False
        assert metadata.can_copy is True

    def test_acl_settings_from_dict(self):
        """Test ACLSettings creation."""
        from codomyrmex.cloud.coda_io.models import ACLSettings

        data = {
            "allowEditorsToChangePermissions": False,
            "allowCopying": True,
            "allowViewersToRequestEditing": True,
        }

        settings = ACLSettings.from_dict(data)

        assert settings.allow_editors_to_change_permissions is False
        assert settings.allow_copying is True
        assert settings.allow_viewers_to_request_editing is True

    def test_principal_to_dict(self):
        """Test Principal serialization."""
        from codomyrmex.cloud.coda_io.models import Principal

        principal = Principal(type="email", email="user@example.com")
        result = principal.to_dict()

        assert result == {"type": "email", "email": "user@example.com"}


@pytest.mark.unit
class TestMutationStatus:
    """Tests for MutationStatus model."""

    def test_mutation_status_completed(self):
        """Test MutationStatus with completed state."""
        from codomyrmex.cloud.coda_io.models import MutationStatus

        data = {"completed": True}
        status = MutationStatus.from_dict(data)

        assert status.completed is True
        assert status.warning is None

    def test_mutation_status_with_warning(self):
        """Test MutationStatus with warning."""
        from codomyrmex.cloud.coda_io.models import MutationStatus

        data = {
            "completed": True,
            "warning": "Some rows were skipped",
        }

        status = MutationStatus.from_dict(data)

        assert status.completed is True
        assert status.warning == "Some rows were skipped"


@pytest.mark.unit
class TestInsertRowsResult:
    """Tests for InsertRowsResult model."""

    def test_insert_rows_result(self):
        """Test InsertRowsResult creation."""
        from codomyrmex.cloud.coda_io.models import InsertRowsResult

        data = {
            "requestId": "abc-123-def",
            "addedRowIds": ["i-row1", "i-row2", "i-row3"],
        }

        result = InsertRowsResult.from_dict(data)

        assert result.request_id == "abc-123-def"
        assert result.added_row_ids == ["i-row1", "i-row2", "i-row3"]


@pytest.mark.unit
class TestDatetimeParsing:
    """Tests for datetime parsing utility."""

    def test_parse_iso_datetime_with_z(self):
        """Test parsing ISO datetime with Z suffix."""
        from codomyrmex.cloud.coda_io.models import _parse_datetime

        result = _parse_datetime("2024-01-15T10:30:00Z")

        assert result is not None
        assert result.year == 2024
        assert result.month == 1
        assert result.day == 15
        assert result.hour == 10
        assert result.minute == 30

    def test_parse_iso_datetime_with_offset(self):
        """Test parsing ISO datetime with timezone offset."""
        from codomyrmex.cloud.coda_io.models import _parse_datetime

        result = _parse_datetime("2024-01-15T10:30:00+00:00")

        assert result is not None
        assert result.year == 2024

    def test_parse_none_returns_none(self):
        """Test parsing None returns None."""
        from codomyrmex.cloud.coda_io.models import _parse_datetime

        result = _parse_datetime(None)
        assert result is None

    def test_parse_invalid_returns_none(self):
        """Test parsing invalid string returns None."""
        from codomyrmex.cloud.coda_io.models import _parse_datetime

        result = _parse_datetime("not a date")
        assert result is None
