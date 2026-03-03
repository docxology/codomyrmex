import pytest

from codomyrmex.cloud.mcp_tools import (
    list_cloud_instances,
    list_s3_buckets,
    upload_file_to_s3,
)


@pytest.mark.unit
def test_list_cloud_instances_error(monkeypatch):
    """Test zero-mock error path for list_cloud_instances."""
    # Ensure environment variables are missing to trigger auth failure
    monkeypatch.delenv("INFOMANIAK_APP_CREDENTIAL_ID", raising=False)
    monkeypatch.delenv("INFOMANIAK_APP_CREDENTIAL_SECRET", raising=False)

    result = list_cloud_instances()
    assert result["status"] == "error"
    assert "Failed to list instances" in result["message"]

@pytest.mark.unit
def test_list_s3_buckets_error(monkeypatch):
    """Test zero-mock error path for list_s3_buckets."""
    monkeypatch.delenv("INFOMANIAK_S3_ACCESS_KEY", raising=False)
    monkeypatch.delenv("INFOMANIAK_S3_SECRET_KEY", raising=False)

    result = list_s3_buckets()
    assert result["status"] == "error"
    assert "Failed to list buckets" in result["message"]

@pytest.mark.unit
def test_upload_file_to_s3_error(monkeypatch):
    """Test zero-mock error path for upload_file_to_s3."""
    monkeypatch.delenv("INFOMANIAK_S3_ACCESS_KEY", raising=False)
    monkeypatch.delenv("INFOMANIAK_S3_SECRET_KEY", raising=False)

    result = upload_file_to_s3("file.txt", "bucket")
    assert result["status"] == "error"
    assert "Failed to upload file" in result["message"]
