"""Unit tests for cloud module expansion."""

import pytest

from _stubs import Stub

try:
    from codomyrmex.cloud import AzureBlobClient, GCSClient, S3Client
    # The cloud module may import successfully but set classes to None
    # when underlying SDKs (boto3, google-cloud-storage, azure) aren't installed
    CLOUD_DEPS_AVAILABLE = (
        S3Client is not None
        and GCSClient is not None
        and AzureBlobClient is not None
    )
except ImportError:
    CLOUD_DEPS_AVAILABLE = False

pytestmark = pytest.mark.skipif(
    not CLOUD_DEPS_AVAILABLE,
    reason="Cloud SDK dependencies (boto3, google-cloud-storage, azure-storage-blob) not installed"
)

@pytest.mark.unit
def test_s3_client_list(monkeypatch):
    """Test S3Client listing objects."""
    mock_s3 = Stub()
    mock_s3.list_objects_v2.return_value = {
        'Contents': [{'Key': 'file1.txt'}, {'Key': 'file2.txt'}]
    }
    monkeypatch.setattr('boto3.client', lambda *a, **kw: mock_s3)

    client = S3Client()
    objects = client.list_objects("my-bucket")
    assert objects == ['file1.txt', 'file2.txt']
    mock_s3.list_objects_v2.assert_called_once_with(Bucket="my-bucket")

@pytest.mark.unit
def test_s3_client_download(monkeypatch):
    """Test S3Client downloading objects."""
    mock_s3 = Stub()
    monkeypatch.setattr('boto3.client', lambda *a, **kw: mock_s3)
    client = S3Client()
    assert client.download_file("bucket", "obj", "local") is True
    mock_s3.download_file.assert_called_once_with("bucket", "obj", "local")

@pytest.mark.unit
def test_gcs_client_list(monkeypatch):
    """Test GCSClient listing blobs."""
    mock_client = Stub()
    mock_blob1 = Stub()
    mock_blob1.name = "blob1"
    mock_blob2 = Stub()
    mock_blob2.name = "blob2"
    mock_client.list_blobs.return_value = [mock_blob1, mock_blob2]
    monkeypatch.setattr('google.cloud.storage.Client', lambda **kw: mock_client)

    client = GCSClient(project="test-project")
    blobs = client.list_blobs("my-bucket")
    assert blobs == ["blob1", "blob2"]
    mock_client.list_blobs.assert_called_once_with("my-bucket")

@pytest.mark.unit
def test_gcs_client_download(monkeypatch):
    """Test GCSClient downloading blobs."""
    mock_client = Stub()
    mock_bucket = Stub()
    mock_client.bucket.return_value = mock_bucket
    mock_blob = Stub()
    mock_bucket.blob.return_value = mock_blob
    monkeypatch.setattr('google.cloud.storage.Client', lambda **kw: mock_client)

    client = GCSClient(project="test-project")
    assert client.download_blob("bucket", "blob", "local") is True
    mock_blob.download_to_filename.assert_called_once_with("local")

@pytest.mark.unit
def test_azure_blob_client_list(monkeypatch):
    """Test AzureBlobClient listing blobs."""
    mock_client = Stub()
    mock_container = Stub()
    mock_client.get_container_client.return_value = mock_container

    mock_blob1 = Stub()
    mock_blob1.name = "azure-blob1"
    mock_container.list_blobs.return_value = [mock_blob1]

    monkeypatch.setattr(
        'codomyrmex.cloud.azure.BlobServiceClient',
        lambda *a, **kw: mock_client
    )
    monkeypatch.setattr(
        'codomyrmex.cloud.azure.DefaultAzureCredential',
        lambda: Stub()
    )

    client = AzureBlobClient(account_url="https://test.blob.core.windows.net")
    blobs = client.list_blobs("my-container")
    assert blobs == ["azure-blob1"]
    mock_container.list_blobs.assert_called_once()
