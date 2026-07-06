"""Unit tests for the cloud module's MCP tools."""

import pytest

from codomyrmex.cloud.mcp_tools import (
    gws_sdk_calendar_list_events,
    gws_sdk_drive_list_files,
    gws_sdk_gmail_list_messages,
    gws_sdk_sheets_get_values,
    list_cloud_instances,
    list_s3_buckets,
    upload_file_to_s3,
)


@pytest.fixture
def mock_gmail_client(monkeypatch):
    class MockClient:
        @classmethod
        def from_env(cls):
            return cls()

        def list_messages(self, query="", max_results=20):
            if query == "error":
                raise Exception("API error")
            return [{"id": "1", "snippet": "Test message"}] * min(max_results, 2)

    monkeypatch.setattr(
        "codomyrmex.cloud.google_workspace.gmail.GoogleGmailClient", MockClient
    )
    return MockClient


def test_gws_sdk_gmail_list_messages_success(mock_gmail_client):
    result = gws_sdk_gmail_list_messages(query="is:unread", max_results=10)

    assert result["status"] == "success"
    assert "messages" in result
    assert result["count"] == 2
    assert result["messages"][0]["id"] == "1"


def test_gws_sdk_gmail_list_messages_error(mock_gmail_client):
    result = gws_sdk_gmail_list_messages(query="error")

    assert result["status"] == "error"
    assert "API error" in result["message"]


def test_gws_sdk_gmail_list_messages_auth_error(monkeypatch):
    class MockClientError:
        @classmethod
        def from_env(cls):
            raise Exception("Missing credentials")

    monkeypatch.setattr(
        "codomyrmex.cloud.google_workspace.gmail.GoogleGmailClient", MockClientError
    )

    result = gws_sdk_gmail_list_messages()

    assert result["status"] == "error"
    assert "Missing credentials" in result["message"]


@pytest.fixture
def mock_drive_client(monkeypatch):
    class MockClient:
        @classmethod
        def from_env(cls):
            return cls()

        def list_files(self, query="", page_size=20):
            if query == "error":
                raise Exception("Drive API error")
            return [{"id": "1", "name": "Document"}] * min(page_size, 2)

    monkeypatch.setattr(
        "codomyrmex.cloud.google_workspace.drive.GoogleDriveClient", MockClient
    )
    return MockClient


def test_gws_sdk_drive_list_files_success(mock_drive_client):
    result = gws_sdk_drive_list_files(query="name contains 'test'", page_size=10)

    assert result["status"] == "success"
    assert "files" in result
    assert result["count"] == 2
    assert result["files"][0]["id"] == "1"


def test_gws_sdk_drive_list_files_error(mock_drive_client):
    result = gws_sdk_drive_list_files(query="error")

    assert result["status"] == "error"
    assert "Drive API error" in result["message"]


@pytest.fixture
def mock_calendar_client(monkeypatch):
    class MockClient:
        @classmethod
        def from_env(cls):
            return cls()

        def list_events(self, calendar_id="primary", time_min="", time_max=""):
            if calendar_id == "error":
                raise Exception("Calendar API error")
            return [{"id": "1", "summary": "Meeting"}]

    monkeypatch.setattr(
        "codomyrmex.cloud.google_workspace.calendar.GoogleCalendarClient", MockClient
    )
    return MockClient


def test_gws_sdk_calendar_list_events_success(mock_calendar_client):
    result = gws_sdk_calendar_list_events(calendar_id="primary")

    assert result["status"] == "success"
    assert "events" in result
    assert result["count"] == 1
    assert result["events"][0]["id"] == "1"


def test_gws_sdk_calendar_list_events_error(mock_calendar_client):
    result = gws_sdk_calendar_list_events(calendar_id="error")

    assert result["status"] == "error"
    assert "Calendar API error" in result["message"]


@pytest.fixture
def mock_sheets_client(monkeypatch):
    class MockClient:
        @classmethod
        def from_env(cls):
            return cls()

        def get_values(self, spreadsheet_id, range_notation):
            if spreadsheet_id == "error":
                raise Exception("Sheets API error")
            return [["A1", "B1"], ["A2", "B2"]]

    monkeypatch.setattr(
        "codomyrmex.cloud.google_workspace.sheets.GoogleSheetsClient", MockClient
    )
    return MockClient


def test_gws_sdk_sheets_get_values_success(mock_sheets_client):
    result = gws_sdk_sheets_get_values(spreadsheet_id="123", range_notation="A1:B2")

    assert result["status"] == "success"
    assert "values" in result
    assert result["range"] == "A1:B2"
    assert len(result["values"]) == 2


def test_gws_sdk_sheets_get_values_error(mock_sheets_client):
    result = gws_sdk_sheets_get_values(spreadsheet_id="error", range_notation="A1:B2")

    assert result["status"] == "error"
    assert "Sheets API error" in result["message"]


class MockInstance:
    def __init__(self, id, name, status, flavor):
        self.id = id
        self.name = name
        self.status = status
        self.flavor = flavor


@pytest.fixture
def mock_compute_client(monkeypatch):
    class MockClient:
        @classmethod
        def from_env(cls):
            return cls()

        def list_instances(self):
            return [
                MockInstance(
                    id="1",
                    name="test-instance",
                    status="ACTIVE",
                    flavor={"original_name": "small"},
                ),
                MockInstance(
                    id="2", name="test-instance-2", status="STOPPED", flavor="large"
                ),
            ]

    monkeypatch.setattr(
        "codomyrmex.cloud.infomaniak.InfomaniakComputeClient", MockClient
    )
    return MockClient


def test_list_cloud_instances_success(mock_compute_client):
    result = list_cloud_instances()

    assert result["status"] == "success"
    assert "instances" in result
    assert result["count"] == 2
    assert result["instances"][0]["id"] == "1"
    assert result["instances"][0]["flavor"] == "small"
    assert result["instances"][1]["flavor"] == "large"


def test_list_cloud_instances_error(monkeypatch):
    class MockClientError:
        @classmethod
        def from_env(cls):
            raise Exception("Auth failed")

    monkeypatch.setattr(
        "codomyrmex.cloud.infomaniak.InfomaniakComputeClient", MockClientError
    )

    result = list_cloud_instances()

    assert result["status"] == "error"
    assert "Auth failed" in result["message"]


@pytest.fixture
def mock_s3_client(monkeypatch):
    class MockClient:
        @classmethod
        def from_env(cls):
            return cls()

        def list_buckets(self):
            return [{"Name": "test-bucket"}, {"Name": "test-bucket-2"}]

        def upload_file(self, file_path, bucket, object_name=None):
            if bucket == "error":
                raise Exception("Upload failed")

    monkeypatch.setattr("codomyrmex.cloud.infomaniak.InfomaniakS3Client", MockClient)
    return MockClient


def test_list_s3_buckets_success(mock_s3_client):
    result = list_s3_buckets()

    assert result["status"] == "success"
    assert "buckets" in result
    assert result["count"] == 2
    assert result["buckets"] == ["test-bucket", "test-bucket-2"]


def test_list_s3_buckets_error(monkeypatch):
    class MockClientError:
        @classmethod
        def from_env(cls):
            raise Exception("Auth failed")

    monkeypatch.setattr(
        "codomyrmex.cloud.infomaniak.InfomaniakS3Client", MockClientError
    )

    result = list_s3_buckets()

    assert result["status"] == "error"
    assert "Auth failed" in result["message"]


def test_upload_file_to_s3_success(mock_s3_client):
    result = upload_file_to_s3(file_path="test.txt", bucket="test-bucket")

    assert result["status"] == "success"
    assert "Successfully uploaded" in result["message"]


def test_upload_file_to_s3_error(mock_s3_client):
    result = upload_file_to_s3(file_path="test.txt", bucket="error")

    assert result["status"] == "error"
    assert "Upload failed" in result["message"]
