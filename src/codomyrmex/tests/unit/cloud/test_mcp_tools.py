import pytest

from codomyrmex.cloud.infomaniak import InfomaniakS3Client
from codomyrmex.cloud.mcp_tools import upload_file_to_s3


class S3ClientStub:
    def __init__(self):
        self.call_count = 0

    def upload_file(self, file_path, bucket, object_name=None):
        self.call_count += 1


def test_upload_file_to_s3_success(monkeypatch):
    stub_client = S3ClientStub()

    def mock_from_env():
        return stub_client

    monkeypatch.setattr(InfomaniakS3Client, "from_env", mock_from_env)

    result = upload_file_to_s3("path/to/file.txt", "my-bucket", "file.txt")

    assert result == {
        "status": "success",
        "message": "Successfully uploaded path/to/file.txt to my-bucket",
    }
    assert stub_client.call_count == 1


def test_upload_file_to_s3_error(monkeypatch):
    def mock_from_env():
        raise ValueError("missing env vars")

    monkeypatch.setattr(InfomaniakS3Client, "from_env", mock_from_env)

    result = upload_file_to_s3("path/to/file.txt", "my-bucket", "file.txt")

    assert result["status"] == "error"
    assert "Failed to upload file" in result["message"]
