"""Unit tests for cloud module expansion."""

from unittest.mock import MagicMock, patch

import pytest

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
def test_s3_client_list():
    """Test S3Client listing objects."""
    with patch('boto3.client') as mock_boto:
        mock_s3 = MagicMock()
        mock_boto.return_value = mock_s3
        mock_s3.list_objects_v2.return_value = {
            'Contents': [{'Key': 'file1.txt'}, {'Key': 'file2.txt'}]
        }

        client = S3Client()
        objects = client.list_objects("my-bucket")
        assert objects == ['file1.txt', 'file2.txt']
        mock_s3.list_objects_v2.assert_called_once_with(Bucket="my-bucket")

@pytest.mark.unit
def test_s3_client_download():
    """Test S3Client downloading objects."""
    with patch('boto3.client') as mock_boto:
        mock_s3 = MagicMock()
        mock_boto.return_value = mock_s3
        client = S3Client()
        assert client.download_file("bucket", "obj", "local") is True
        mock_s3.download_file.assert_called_once_with("bucket", "obj", "local")

@pytest.mark.unit
def test_gcs_client_list():
    """Test GCSClient listing blobs."""
    with patch('google.cloud.storage.Client') as mock_storage:
        mock_client = MagicMock()
        mock_storage.return_value = mock_client
        mock_blob1 = MagicMock()
        mock_blob1.name = "blob1"
        mock_blob2 = MagicMock()
        mock_blob2.name = "blob2"
        mock_client.list_blobs.return_value = [mock_blob1, mock_blob2]

        client = GCSClient(project="test-project")
        blobs = client.list_blobs("my-bucket")
        assert blobs == ["blob1", "blob2"]
        mock_client.list_blobs.assert_called_once_with("my-bucket")

@pytest.mark.unit
def test_gcs_client_download():
    """Test GCSClient downloading blobs."""
    with patch('google.cloud.storage.Client') as mock_storage:
        mock_client = MagicMock()
        mock_storage.return_value = mock_client
        mock_bucket = MagicMock()
        mock_client.bucket.return_value = mock_bucket
        mock_blob = MagicMock()
        mock_bucket.blob.return_value = mock_blob

        client = GCSClient(project="test-project")
        assert client.download_blob("bucket", "blob", "local") is True
        mock_blob.download_to_filename.assert_called_once_with("local")

@pytest.mark.unit
def test_azure_blob_client_list():
    """Test AzureBlobClient listing blobs."""
    with patch('codomyrmex.cloud.azure.BlobServiceClient') as mock_blob_service, \
         patch('codomyrmex.cloud.azure.DefaultAzureCredential') as mock_cred:
        mock_client = MagicMock()
        mock_blob_service.return_value = mock_client
        mock_container = MagicMock()
        mock_client.get_container_client.return_value = mock_container

        mock_blob1 = MagicMock()
        mock_blob1.name = "azure-blob1"
        mock_container.list_blobs.return_value = [mock_blob1]

        client = AzureBlobClient(account_url="https://test.blob.core.windows.net")
        blobs = client.list_blobs("my-container")
        assert blobs == ["azure-blob1"]
        mock_container.list_blobs.assert_called_once()
