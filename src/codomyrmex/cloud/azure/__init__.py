"""Azure integration submodule."""

import os
from datetime import UTC
from typing import Any, Optional

from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient, ContentSettings

from codomyrmex.cloud.common import StorageClient
from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)

class AzureBlobClient(StorageClient):
    """Wrapper for Azure Blob Storage operations."""

    def __init__(self, account_url: str | None = None, client: BlobServiceClient | None = None):
        if client:
            self.client = client
        elif account_url:
            self.client = BlobServiceClient(account_url, credential=DefaultAzureCredential())
        else:
            env_url = os.environ.get("AZURE_STORAGE_ACCOUNT_URL")
            if env_url:
                self.client = BlobServiceClient(env_url, credential=DefaultAzureCredential())
            else:
                self.client = None
                logger.warning("Azure account_url not provided and AZURE_STORAGE_ACCOUNT_URL not set.")

    def list_buckets(self) -> list[str]:
        """List containers (buckets)."""
        if not self.client:
            return []
        try:
            containers = self.client.list_containers()
            return [container.name for container in containers]
        except Exception as e:
            logger.error(f"Azure list_buckets (containers) error: {e}")
            return []

    def create_bucket(self, name: str, region: str | None = None) -> bool:
        """Create a container."""
        if not self.client:
            return False
        try:
            self.client.create_container(name)
            return True
        except Exception as e:
            logger.error(f"Azure create_bucket (container) error: {e}")
            return False

    def delete_bucket(self, name: str) -> bool:
        """Delete a container."""
        if not self.client:
            return False
        try:
            self.client.delete_container(name)
            return True
        except Exception as e:
            logger.error(f"Azure delete_bucket (container) error: {e}")
            return False

    def bucket_exists(self, name: str) -> bool:
        """Check if a container exists."""
        if not self.client:
            return False
        try:
            container_client = self.client.get_container_client(name)
            return container_client.exists()
        except Exception as e:
            logger.error(f"Azure bucket_exists (container) error: {e}")
            return False

    def upload_file(self, bucket: str, key: str, file_path: str, content_type: str | None = None) -> bool:
        """Upload a blob from local disk."""
        if not self.client:
            return False
        try:
            blob_client = self.client.get_blob_client(container=bucket, blob=key)
            content_settings = ContentSettings(content_type=content_type) if content_type else None
            with open(file_path, "rb") as data:
                blob_client.upload_blob(data, overwrite=True, content_settings=content_settings)
            return True
        except Exception as e:
            logger.error(f"Azure upload_file error: {e}")
            return False

    def download_file(self, bucket: str, key: str, file_path: str) -> bool:
        """Download a blob to local disk."""
        if not self.client:
            return False
        try:
            blob_client = self.client.get_blob_client(container=bucket, blob=key)
            with open(file_path, "wb") as download_file:
                download_file.write(blob_client.download_blob().readall())
            return True
        except Exception as e:
            logger.error(f"Azure download_file error: {e}")
            return False

    def list_objects(self, bucket: str, prefix: str | None = None) -> list[str]:
        """List blobs in a container."""
        if not self.client:
            return []
        try:
            container_client = self.client.get_container_client(bucket)
            blobs = container_client.list_blobs(name_starts_with=prefix)
            return [blob.name for blob in blobs]
        except Exception as e:
            logger.error(f"Azure list_objects error: {e}")
            return []

    def delete_object(self, bucket: str, key: str) -> bool:
        """Delete a blob."""
        if not self.client:
            return False
        try:
            blob_client = self.client.get_blob_client(container=bucket, blob=key)
            blob_client.delete_blob()
            return True
        except Exception as e:
            logger.error(f"Azure delete_object error: {e}")
            return False

    def get_object_metadata(self, bucket: str, key: str) -> dict[str, Any]:
        """Get blob metadata."""
        if not self.client:
            return {}
        try:
            blob_client = self.client.get_blob_client(container=bucket, blob=key)
            properties = blob_client.get_blob_properties()
            return properties.metadata if properties.metadata else {}
        except Exception as e:
            logger.error(f"Azure get_object_metadata error: {e}")
            return {}

    def generate_presigned_url(
        self,
        bucket: str,
        key: str,
        expires_in: int = 3600,
        operation: str = "get_object",
    ) -> str:
        """Generate a SAS URL."""
        from datetime import datetime, timedelta, timezone

        from azure.storage.blob import BlobSasPermissions, generate_blob_sas

        if not self.client:
            return ""

        # Note: generate_blob_sas requires account_key.
        # If using DefaultAzureCredential, user should use User Delegation SAS or other methods.
        # We provide a basic implementation but warn if account_key is missing.
        account_key = getattr(self.client.credential, 'account_key', None)
        if not account_key:
            logger.warning("generate_blob_sas requires an account_key which is not available on this credential.")
            return ""

        try:
            permission = BlobSasPermissions(read=True) if operation == "get_object" else BlobSasPermissions(write=True)
            sas_token = generate_blob_sas(
                account_name=self.client.account_name,
                container_name=bucket,
                blob_name=key,
                account_key=account_key,
                permission=permission,
                expiry=datetime.now(UTC) + timedelta(seconds=expires_in)
            )
            return f"{self.client.url}{bucket}/{key}?{sas_token}"
        except Exception as e:
            logger.error(f"Azure generate_presigned_url error: {e}")
            return ""

    # Legacy methods for backward compatibility
    def upload_blob(self, container_name: str, blob_name: str, file_path: str) -> bool:
        return self.upload_file(container_name, blob_name, file_path)

    def list_blobs(self, container_name: str) -> list[str]:
        return self.list_objects(container_name)

    def download_blob(self, container_name: str, blob_name: str, file_path: str) -> bool:
        return self.download_file(container_name, blob_name, file_path)

    def get_metadata(self, container_name: str, blob_name: str) -> dict:
        return self.get_object_metadata(container_name, blob_name)

    def ensure_container(self, container_name: str) -> bool:
        if self.bucket_exists(container_name):
            return True
        return self.create_bucket(container_name)
