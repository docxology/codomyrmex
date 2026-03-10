"""
Unit tests for unified cloud storage clients.

Uses strictly zero-stub tests with the Stub class.
"""

import sys

import pytest
from _stubs import Stub

# Zero-stub strategy: Stub out optional cloud SDKs in sys.modules
# before importing the client wrappers. This allows testing the logic
# in the wrappers without requiring the actual SDKs to be installed.
stub_boto3 = Stub()
stub_botocore = Stub()
stub_google = Stub()
stub_azure = Stub()

sys.modules["boto3"] = stub_boto3
sys.modules["botocore"] = stub_botocore
sys.modules["botocore.exceptions"] = stub_botocore.exceptions
sys.modules["google"] = stub_google
sys.modules["google.cloud"] = stub_google.cloud
sys.modules["google.cloud.storage"] = stub_google.cloud.storage
sys.modules["azure"] = stub_azure
sys.modules["azure.identity"] = stub_azure.identity
sys.modules["azure.storage"] = stub_azure.storage
sys.modules["azure.storage.blob"] = stub_azure.storage.blob

from codomyrmex.cloud.aws import S3Client
from codomyrmex.cloud.azure import AzureBlobClient
from codomyrmex.cloud.gcp import GCSClient


class TestUnifiedStorageClients:
    """Tests for unified storage client implementations."""

    @pytest.fixture
    def stub_boto3_session(self):
        """Create a stub boto3 session."""
        session = Stub()
        session.client.return_value = Stub()
        return session

    @pytest.fixture
    def stub_gcs_client(self):
        """Create a stub GCS client."""
        return Stub()

    @pytest.fixture
    def stub_azure_client(self):
        """Create a stub Azure BlobServiceClient."""
        client = Stub()
        client.account_name = "testaccount"
        client.url = "https://testaccount.blob.core.windows.net/"
        client.credential = Stub(account_key="testkey")
        return client

    # -----------------------------------------------------------------
    # AWS S3Client Tests
    # -----------------------------------------------------------------

    def test_s3_list_buckets(self, stub_boto3_session):
        """Test S3Client list_buckets."""
        s3_stub = stub_boto3_session.client.return_value
        s3_stub.list_buckets.return_value = {
            "Buckets": [{"Name": "bucket1"}, {"Name": "bucket2"}]
        }

        client = S3Client(session=stub_boto3_session)
        buckets = client.list_buckets()

        assert buckets == ["bucket1", "bucket2"]
        s3_stub.list_buckets.assert_called_once()

    def test_s3_create_bucket(self, stub_boto3_session):
        """Test S3Client create_bucket."""
        s3_stub = stub_boto3_session.client.return_value
        client = S3Client(session=stub_boto3_session)

        assert client.create_bucket("new-bucket") is True
        s3_stub.create_bucket.assert_called_once_with(Bucket="new-bucket")

    def test_s3_upload_file(self, stub_boto3_session, tmp_path):
        """Test S3Client upload_file."""
        s3_stub = stub_boto3_session.client.return_value
        client = S3Client(session=stub_boto3_session)

        test_file = tmp_path / "test.txt"
        test_file.write_text("hello")

        assert (
            client.upload_file(
                "my-bucket", "my-key", str(test_file), content_type="text/plain"
            )
            is True
        )
        s3_stub.upload_file.assert_called_once_with(
            str(test_file),
            "my-bucket",
            "my-key",
            ExtraArgs={"ContentType": "text/plain"},
        )

    # -----------------------------------------------------------------
    # GCP GCSClient Tests
    # -----------------------------------------------------------------

    def test_gcs_list_buckets(self, stub_gcs_client):
        """Test GCSClient list_buckets."""
        stub_gcs_client.list_buckets.return_value = [
            Stub(name="bucket1"),
            Stub(name="bucket2"),
        ]

        client = GCSClient(client=stub_gcs_client)
        buckets = client.list_buckets()

        assert buckets == ["bucket1", "bucket2"]
        stub_gcs_client.list_buckets.assert_called_once()

    def test_gcs_upload_file(self, stub_gcs_client, tmp_path):
        """Test GCSClient upload_file."""
        bucket_stub = Stub()
        blob_stub = Stub()
        stub_gcs_client.bucket.return_value = bucket_stub
        bucket_stub.blob.return_value = blob_stub

        client = GCSClient(client=stub_gcs_client)
        test_file = tmp_path / "test.txt"
        test_file.write_text("hello")

        assert client.upload_file("my-bucket", "my-key", str(test_file)) is True
        stub_gcs_client.bucket.assert_called_once_with("my-bucket")
        bucket_stub.blob.assert_called_once_with("my-key")
        blob_stub.upload_from_filename.assert_called_once_with(
            str(test_file), content_type=None
        )

    # -----------------------------------------------------------------
    # Azure AzureBlobClient Tests
    # -----------------------------------------------------------------

    def test_azure_list_buckets(self, stub_azure_client):
        """Test AzureBlobClient list_buckets (containers)."""
        stub_azure_client.list_containers.return_value = [
            Stub(name="container1"),
            Stub(name="container2"),
        ]

        client = AzureBlobClient(client=stub_azure_client)
        containers = client.list_buckets()

        assert containers == ["container1", "container2"]
        stub_azure_client.list_containers.assert_called_once()

    def test_azure_upload_file(self, stub_azure_client, tmp_path):
        """Test AzureBlobClient upload_file."""
        blob_client_stub = Stub()
        stub_azure_client.get_blob_client.return_value = blob_client_stub

        client = AzureBlobClient(client=stub_azure_client)
        test_file = tmp_path / "test.txt"
        test_file.write_text("hello")

        assert client.upload_file("my-container", "my-blob", str(test_file)) is True
        stub_azure_client.get_blob_client.assert_called_once_with(
            container="my-container", blob="my-blob"
        )
        blob_client_stub.upload_blob.assert_called_once()
