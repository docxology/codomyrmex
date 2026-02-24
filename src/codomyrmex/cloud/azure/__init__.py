"""Azure integration submodule."""

import logging
import os
from typing import Optional

from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient

logger = logging.getLogger(__name__)

class AzureBlobClient:
    """Wrapper for Azure Blob Storage operations."""

    def __init__(self, account_url: str | None = None):
        """Execute   Init   operations natively."""
        if not account_url:
            account_url = os.environ.get("AZURE_STORAGE_ACCOUNT_URL")

        if account_url:
            self.client = BlobServiceClient(account_url, credential=DefaultAzureCredential())
        else:
            self.client = None
            logger.warning("Azure account_url not provided and AZURE_STORAGE_ACCOUNT_URL not set.")

    def upload_blob(self, container_name: str, blob_name: str, file_path: str) -> bool:
        """Upload a blob to a container."""
        if not self.client:
            return False

        try:
            blob_client = self.client.get_blob_client(container=container_name, blob=blob_name)
            with open(file_path, "rb") as data:
                blob_client.upload_blob(data, overwrite=True)
            return True
        except Exception as e:
            logger.error(f"Azure upload error: {e}")
            return False

    def list_blobs(self, container_name: str) -> list[str]:
        """List blobs in a container."""
        if not self.client:
            return []

        try:
            container_client = self.client.get_container_client(container_name)
            blob_list = container_client.list_blobs()
            return [blob.name for blob in blob_list]
        except Exception as e:
            logger.error(f"Azure list error: {e}")
            return []

    def download_blob(self, container_name: str, blob_name: str, file_path: str) -> bool:
        """Download a blob from a container."""
        if not self.client:
            return False
        try:
            blob_client = self.client.get_blob_client(container=container_name, blob=blob_name)
            with open(file_path, "wb") as download_file:
                download_file.write(blob_client.download_blob().readall())
            return True
        except Exception as e:
            logger.error(f"Azure download error: {e}")
            return False

    def get_metadata(self, container_name: str, blob_name: str) -> dict:
        """Get blob metadata."""
        if not self.client:
            return {}
        try:
            blob_client = self.client.get_blob_client(container=container_name, blob=blob_name)
            return blob_client.get_blob_properties().metadata
        except Exception as e:
            logger.error(f"Azure metadata error: {e}")
            return {}

    def ensure_container(self, container_name: str) -> bool:
        """Ensure a container exists."""
        if not self.client:
            return False
        try:
            container_client = self.client.get_container_client(container_name)
            if not container_client.exists():
                self.client.create_container(container_name)
            return True
        except Exception as e:
            logger.error(f"Azure container creation error: {e}")
            return False
