"""Local contracts of actual cloud SDK clients, without account/API access.

The declared ``cloud`` extra is required. Clients use synthetic AWS/Azure keys
or GCS AnonymousCredentials and explicitly selected temporary configuration.
These checks cover protocol compatibility, local signing/resource metadata and
filesystem failures. Successful cloud read/write acceptance requires separate
explicitly authorized integration evidence; it is not simulated here.
"""

from __future__ import annotations

import base64
import os
import sys
import types
from collections.abc import Iterator
from pathlib import Path
from typing import TYPE_CHECKING
from urllib.parse import parse_qs, urlsplit

import pytest

from codomyrmex.cloud.common import StorageClient

if TYPE_CHECKING:
    from codomyrmex.cloud.aws import S3Client
    from codomyrmex.cloud.azure import AzureBlobClient
    from codomyrmex.cloud.gcp import GCSClient

pytestmark = pytest.mark.unit


@pytest.fixture(autouse=True)
def isolated_cloud_configuration(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """No operator AWS/Google/Azure configuration is part of the local controls."""
    for name in list(os.environ):
        if name.startswith(("AWS_", "AZURE_")):
            monkeypatch.delenv(name, raising=False)
    config = tmp_path / "aws-config"
    config.write_text(
        "[default]\ns3 =\n    signature_version = s3v4\n", encoding="utf-8"
    )
    monkeypatch.setenv("AWS_CONFIG_FILE", str(config))
    monkeypatch.setenv(
        "AWS_SHARED_CREDENTIALS_FILE", str(tmp_path / "absent-aws-creds")
    )
    monkeypatch.setenv("AWS_EC2_METADATA_DISABLED", "true")
    monkeypatch.setenv(
        "GOOGLE_APPLICATION_CREDENTIALS", str(tmp_path / "absent-adc.json")
    )
    monkeypatch.setenv("CLOUDSDK_CONFIG", str(tmp_path / "gcloud"))


@pytest.fixture
def s3_client() -> Iterator[S3Client]:
    boto3 = pytest.importorskip("boto3")
    from codomyrmex.cloud.aws import S3Client

    assert isinstance(sys.modules["boto3"], types.ModuleType)
    session = boto3.Session(
        aws_access_key_id="local-unit-access",
        aws_secret_access_key="local-unit-secret",  # pragma: allowlist secret
        region_name="us-east-1",
    )
    client = S3Client(region_name="us-east-1", session=session)
    try:
        yield client
    finally:
        client.client.close()


@pytest.fixture
def gcs_client() -> Iterator[GCSClient]:
    storage = pytest.importorskip("google.cloud.storage")
    from google.auth.credentials import AnonymousCredentials

    from codomyrmex.cloud.gcp import GCSClient

    assert isinstance(sys.modules["google.cloud.storage"], types.ModuleType)
    sdk = storage.Client(
        project="local-unit-project", credentials=AnonymousCredentials()
    )
    try:
        yield GCSClient(client=sdk)
    finally:
        sdk.close()


@pytest.fixture
def azure_client() -> Iterator[AzureBlobClient]:
    blob_sdk = pytest.importorskip("azure.storage.blob")
    pytest.importorskip("azure.identity")
    from codomyrmex.cloud.azure import AzureBlobClient

    assert isinstance(sys.modules["azure.storage.blob"], types.ModuleType)
    key = base64.b64encode(b"local-unit-key-material-only" * 2).decode("ascii")
    sdk = blob_sdk.BlobServiceClient(
        account_url="https://localunitaccount.blob.core.windows.net", credential=key
    )
    try:
        yield AzureBlobClient(client=sdk)
    finally:
        sdk.close()


class TestUnifiedStorageClients:
    """Exercise real SDK boundaries without replacing modules or transports."""

    def test_s3_real_service_model_and_region(self, s3_client: S3Client) -> None:
        import boto3

        assert isinstance(s3_client, StorageClient)
        assert isinstance(s3_client.session, boto3.Session)
        model = s3_client.client.meta.service_model
        assert model.service_name == "s3"
        assert {"ListBuckets", "CreateBucket", "PutObject"} <= set(
            model.operation_names
        )
        assert s3_client.client.meta.region_name == "us-east-1"
        assert s3_client.session.get_credentials().method == "explicit"

    @pytest.mark.parametrize("operation", ["get_object", "put_object"])
    def test_s3_local_signing_preserves_object_identity(
        self, s3_client: S3Client, operation: str
    ) -> None:
        """Presigning is local serialization, not cloud access or authorization."""
        signed = s3_client.generate_presigned_url(
            "local-unit-bucket",
            "folder/report.txt",
            expires_in=120,
            operation=operation,
        )
        parts = urlsplit(signed)
        query = parse_qs(parts.query)
        assert parts.scheme == "https"
        assert parts.path.endswith("/folder/report.txt")
        assert "local-unit-bucket" in parts.netloc or parts.path.startswith(
            "/local-unit-bucket/"
        )
        assert query["X-Amz-Algorithm"] == ["AWS4-HMAC-SHA256"]
        assert query["X-Amz-Expires"] == ["120"]
        assert query["X-Amz-Credential"][0].startswith("local-unit-access/")
        assert len(query["X-Amz-Signature"][0]) == 64

    def test_s3_missing_upload_file_is_a_real_filesystem_failure(
        self, s3_client: S3Client, tmp_path: Path
    ) -> None:
        """The SDK stats the file before submitting any transfer request."""
        missing = tmp_path / "missing.txt"
        with pytest.raises(FileNotFoundError):
            s3_client.upload_file("local-unit-bucket", "key", str(missing))
        assert not missing.exists()

    def test_gcs_anonymous_client_and_local_resource_metadata(
        self, gcs_client: GCSClient
    ) -> None:
        from google.auth.credentials import AnonymousCredentials
        from google.cloud import storage

        assert isinstance(gcs_client, StorageClient)
        assert isinstance(gcs_client.client, storage.Client)
        assert isinstance(gcs_client.client._credentials, AnonymousCredentials)
        assert gcs_client.client.project == "local-unit-project"
        bucket = gcs_client.client.bucket("local-unit-bucket")
        blob = bucket.blob("folder/report.txt")
        assert bucket.client is gcs_client.client
        assert blob.bucket is bucket
        assert blob.name == "folder/report.txt"
        assert blob.path == "/b/local-unit-bucket/o/folder%2Freport.txt"

    @pytest.mark.parametrize("directory", [False, True])
    def test_gcs_invalid_upload_file_is_denied_before_api_access(
        self, gcs_client: GCSClient, tmp_path: Path, directory: bool
    ) -> None:
        source = tmp_path / "invalid-input"
        if directory:
            source.mkdir()
        assert not gcs_client.upload_file("local-unit-bucket", "key", str(source))
        assert source.is_dir() if directory else not source.exists()

    def test_gcs_anonymous_credentials_cannot_sign(self, gcs_client: GCSClient) -> None:
        """Missing local signing capability returns the documented empty result."""
        assert gcs_client.generate_presigned_url("local-unit-bucket", "key") == ""

    def test_azure_actual_client_and_local_resource_metadata(
        self, azure_client: AzureBlobClient
    ) -> None:
        from azure.storage.blob import BlobServiceClient

        assert isinstance(azure_client, StorageClient)
        assert isinstance(azure_client.client, BlobServiceClient)
        assert azure_client.client.account_name == "localunitaccount"
        blob = azure_client.client.get_blob_client(
            "local-unit-container", "folder/report.txt"
        )
        try:
            assert blob.container_name == "local-unit-container"
            assert blob.blob_name == "folder/report.txt"
            assert urlsplit(blob.url).path == "/local-unit-container/folder/report.txt"
        finally:
            blob.close()

    @pytest.mark.parametrize(
        ("operation", "permission"), [("get_object", "r"), ("put_object", "w")]
    )
    def test_azure_local_sas_signing_preserves_permissions(
        self, azure_client: AzureBlobClient, operation: str, permission: str
    ) -> None:
        signed = azure_client.generate_presigned_url(
            "local-unit-container",
            "folder/report.txt",
            expires_in=120,
            operation=operation,
        )
        parts = urlsplit(signed)
        query = parse_qs(parts.query)
        assert parts.netloc == "localunitaccount.blob.core.windows.net"
        assert parts.path == "/local-unit-container/folder/report.txt"
        assert query["sp"] == [permission]
        assert query["sr"] == ["b"]
        assert query["sig"][0]
        assert query["se"][0]

    @pytest.mark.parametrize("directory", [False, True])
    def test_azure_invalid_upload_file_is_denied_before_api_access(
        self, azure_client: AzureBlobClient, tmp_path: Path, directory: bool
    ) -> None:
        source = tmp_path / "invalid-input"
        if directory:
            source.mkdir()
        assert not azure_client.upload_file("local-unit-container", "key", str(source))
        assert source.is_dir() if directory else not source.exists()

    def test_azure_unconfigured_client_denies_operations(self) -> None:
        """No account URL means no client or credential-chain acquisition."""
        pytest.importorskip("azure.storage.blob")
        pytest.importorskip("azure.identity")
        from codomyrmex.cloud.azure import AzureBlobClient

        client = AzureBlobClient()
        assert client.client is None
        assert client.list_buckets() == []
        assert not client.create_bucket("local-unit-container")
        assert not client.delete_bucket("local-unit-container")
        assert not client.bucket_exists("local-unit-container")
        assert client.list_objects("local-unit-container") == []
        assert not client.delete_object("local-unit-container", "key")
        assert client.get_object_metadata("local-unit-container", "key") == {}
        assert client.generate_presigned_url("local-unit-container", "key") == ""
