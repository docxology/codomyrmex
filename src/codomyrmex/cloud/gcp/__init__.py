"""GCP integration submodule."""

import logging
from typing import Optional

from google.cloud import storage

logger = logging.getLogger(__name__)

class GCSClient:
    """Wrapper for Google Cloud Storage operations."""

    def __init__(self, project: str | None = None):
        """Execute   Init   operations natively."""
        self.client = storage.Client(project=project)

    def upload_blob(self, bucket_name: str, source_file_name: str, destination_blob_name: str) -> bool:
        """Uploads a file to the bucket."""
        try:
            bucket = self.client.bucket(bucket_name)
            blob = bucket.blob(destination_blob_name)
            blob.upload_from_filename(source_file_name)
            return True
        except Exception as e:
            logger.error(f"GCS upload error: {e}")
            return False

    def list_blobs(self, bucket_name: str) -> list[str]:
        """Lists all the blobs in the bucket."""
        try:
            blobs = self.client.list_blobs(bucket_name)
            return [blob.name for blob in blobs]
        except Exception as e:
            logger.error(f"GCS list error: {e}")
            return []

    def download_blob(self, bucket_name: str, source_blob_name: str, destination_file_name: str) -> bool:
        """Downloads a blob from the bucket."""
        try:
            bucket = self.client.bucket(bucket_name)
            blob = bucket.blob(source_blob_name)
            blob.download_to_filename(destination_file_name)
            return True
        except Exception as e:
            logger.error(f"GCS download error: {e}")
            return False

    def get_metadata(self, bucket_name: str, blob_name: str) -> dict:
        """Get blob metadata."""
        try:
            bucket = self.client.bucket(bucket_name)
            blob = bucket.get_blob(blob_name)
            return blob.metadata if blob else {}
        except Exception as e:
            logger.error(f"GCS metadata error: {e}")
            return {}

    def ensure_bucket(self, bucket_name: str, location: str = "US") -> bool:
        """Ensure a GCS bucket exists."""
        try:
            self.client.get_bucket(bucket_name)
            return True
        except Exception:
            try:
                self.client.create_bucket(bucket_name, location=location)
                return True
            except Exception as e:
                logger.error(f"GCS bucket creation error: {e}")
                return False
