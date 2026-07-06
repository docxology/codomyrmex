from codomyrmex.cloud.mcp_tools import gws_sdk_drive_list_files


def test_gws_sdk_drive_list_files_success(monkeypatch):
    """Test successful listing of Google Drive files."""

    class DummyClient:
        def list_files(self, query: str = "", page_size: int = 20):
            return [{"id": "1", "name": "test.txt"}]

    # Mock from_env directly on the GoogleDriveClient class
    from codomyrmex.cloud.google_workspace.drive import GoogleDriveClient

    monkeypatch.setattr(GoogleDriveClient, "from_env", DummyClient)

    result = gws_sdk_drive_list_files(query="name contains 'test'", page_size=10)

    assert result["status"] == "success"
    assert result["files"] == [{"id": "1", "name": "test.txt"}]
    assert result["count"] == 1


def test_gws_sdk_drive_list_files_error(monkeypatch):
    """Test error handling when listing Google Drive files."""

    class DummyClient:
        def list_files(self, query: str = "", page_size: int = 20):
            raise Exception("API Error")

    # Mock from_env directly on the GoogleDriveClient class
    from codomyrmex.cloud.google_workspace.drive import GoogleDriveClient

    monkeypatch.setattr(GoogleDriveClient, "from_env", DummyClient)

    result = gws_sdk_drive_list_files(query="name contains 'test'", page_size=10)

    assert result["status"] == "error"
    assert result["message"] == "API Error"
