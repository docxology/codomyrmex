"""Tests for cloud MCP tools."""

from typing import Any

import pytest
from _stubs import Stub

from codomyrmex.cloud.infomaniak.object_storage.client import InfomaniakS3Client
from codomyrmex.cloud.mcp_tools import list_s3_buckets


def test_list_s3_buckets_success(
    monkeypatch: pytest.MonkeyPatch, stub_s3_client: Stub, infomaniak_s3_env: Any
) -> None:
    """list_s3_buckets returns a success response with a list of buckets."""

    # Set up the stub s3 client to return the exact structure expected by list_buckets
    stub_s3_client.list_buckets.return_value = {
        "Buckets": [{"Name": "bucket-1"}, {"Name": "bucket-2"}]
    }

    def mock_from_env() -> InfomaniakS3Client:
        # Use the un-mocked method, which will call the stub S3 client correctly.
        return InfomaniakS3Client(client=stub_s3_client)

    monkeypatch.setattr(InfomaniakS3Client, "from_env", mock_from_env)

    result = list_s3_buckets()

    assert result["status"] == "success"
    assert result["buckets"] == ["bucket-1", "bucket-2"]
    assert result["count"] == 2


def test_list_s3_buckets_error(
    monkeypatch: pytest.MonkeyPatch, infomaniak_s3_env: Any
) -> None:
    """list_s3_buckets handles exceptions properly and returns an error message."""

    def mock_from_env() -> InfomaniakS3Client:
        raise ValueError("Invalid S3 credentials")

    monkeypatch.setattr(InfomaniakS3Client, "from_env", mock_from_env)

    result = list_s3_buckets()

    assert result["status"] == "error"
    assert "Failed to list buckets" in result["message"]
    assert "Invalid S3 credentials" in result["message"]
