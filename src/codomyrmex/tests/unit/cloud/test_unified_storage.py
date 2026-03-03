"""
Unit tests for unified cloud storage clients.

Uses strictly zero-mock tests with the Stub class.
"""

import pytest
from _stubs import Stub

from codomyrmex.cloud.aws import S3Client
from codomyrmex.cloud.azure import AzureBlobClient
from codomyrmex.cloud.gcp import GCSClient


class TestUnifiedStorageClients:
    """Tests for unified storage client implementations."""

    @pytest.fixture
    def mock_boto3_session(self):
        """Create a stub boto3 session."""
        session = Stub()
        session.client.return_value = Stub()
        return session

    @pytest.fixture
    def mock_gcs_client(self):
        """Create a stub GCS client."""
        return Stub()

    @pytest.fixture
    def mock_azure_client(self):
        """Create a stub Azure BlobServiceClient."""
        client = Stub()
        client.account_name = "testaccount"
        client.url = "https://testaccount.blob.core.windows.net/"
        client.credential = Stub(account_key="testkey")
        return client

    # -----------------------------------------------------------------
    # AWS S3Client Tests
    # -----------------------------------------------------------------

    def test_s3_list_buckets(self, mock_boto3_session):
        """Test S3Client list_buckets."""
        s3_mock = mock_boto3_session.client.return_value
        s3_mock.list_buckets.return_value = {
            "Buckets": [{"Name": "bucket1"}, {"Name": "bucket2"}]
        }

        client = S3Client(session=mock_boto3_session)
        buckets = client.list_buckets()

        assert buckets == ["bucket1", "bucket2"]
        s3_mock.list_buckets.assert_called_once()

    def test_s3_create_bucket(self, mock_boto3_session):
        """Test S3Client create_bucket."""
        s3_mock = mock_boto3_session.client.return_value
        client = S3Client(session=mock_boto3_session)

        assert client.create_bucket("new-bucket") is True
        s3_mock.create_bucket.assert_called_once_with(Bucket="new-bucket")

    def test_s3_upload_file(self, mock_boto3_session, tmp_path):
        """Test S3Client upload_file."""
        s3_mock = mock_boto3_session.client.return_value
        client = S3Client(session=mock_boto3_session)

        test_file = tmp_path / "test.txt"
        test_file.write_text("hello")

        assert (
            client.upload_file(
                "my-bucket", "my-key", str(test_file), content_type="text/plain"
            )
            is True
        )
        s3_mock.upload_file.assert_called_once_with(
            str(test_file),
            "my-bucket",
            "my-key",
            ExtraArgs={"ContentType": "text/plain"},
        )

    # -----------------------------------------------------------------
    # GCP GCSClient Tests
    # -----------------------------------------------------------------

    def test_gcs_list_buckets(self, mock_gcs_client):
        """Test GCSClient list_buckets."""
        mock_gcs_client.list_buckets.return_value = [
            Stub(name="bucket1"),
            Stub(name="bucket2"),
        ]

        client = GCSClient(client=mock_gcs_client)
        buckets = client.list_buckets()

        assert buckets == ["bucket1", "bucket2"]
        mock_gcs_client.list_buckets.assert_called_once()

    def test_gcs_upload_file(self, mock_gcs_client, tmp_path):
        """Test GCSClient upload_file."""
        bucket_mock = Stub()
        blob_mock = Stub()
        mock_gcs_client.bucket.return_value = bucket_mock
        bucket_mock.blob.return_value = blob_mock

        client = GCSClient(client=mock_gcs_client)
        test_file = tmp_path / "test.txt"
        test_file.write_text("hello")

        assert client.upload_file("my-bucket", "my-key", str(test_file)) is True
        mock_gcs_client.bucket.assert_called_once_with("my-bucket")
        bucket_mock.blob.assert_called_once_with("my-key")
        blob_mock.upload_from_filename.assert_called_once_with(
            str(test_file), content_type=None
        )

    # -----------------------------------------------------------------
    # Azure AzureBlobClient Tests
    # -----------------------------------------------------------------

    def test_azure_list_buckets(self, mock_azure_client):
        """Test AzureBlobClient list_buckets (containers)."""
        mock_azure_client.list_containers.return_value = [
            Stub(name="container1"),
            Stub(name="container2"),
        ]

        client = AzureBlobClient(client=mock_azure_client)
        containers = client.list_buckets()

        assert containers == ["container1", "container2"]
        mock_azure_client.list_containers.assert_called_once()

    def test_azure_upload_file(self, mock_azure_client, tmp_path):
        """Test AzureBlobClient upload_file."""
        blob_client_mock = Stub()
        mock_azure_client.get_blob_client.return_value = blob_client_mock

        client = AzureBlobClient(client=mock_azure_client)
        test_file = tmp_path / "test.txt"
        test_file.write_text("hello")

        assert client.upload_file("my-container", "my-blob", str(test_file)) is True
        mock_azure_client.get_blob_client.assert_called_once_with(
            container="my-container", blob="my-blob"
        )
        blob_client_mock.upload_blob.assert_called_once()
