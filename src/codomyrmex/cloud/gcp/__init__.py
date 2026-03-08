"""GCP integration submodule."""

from typing import Any, Optional

from google.cloud import storage

from codomyrmex.cloud.common import StorageClient
from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


class GCSClient(StorageClient):
    """Wrapper for Google Cloud Storage operations."""

    def __init__(
        self, project: str | None = None, client: storage.Client | None = None
    ):
        self.client = client or storage.Client(project=project)

    def list_buckets(self) -> list[str]:
        """List storage buckets."""
        try:
            buckets = self.client.list_buckets()
            return [bucket.name for bucket in buckets]
        except Exception as e:
            logger.error(f"GCS list_buckets error: {e}")
            return []

    def create_bucket(self, name: str, region: str | None = "US") -> bool:
        """Create a bucket."""
        try:
            self.client.create_bucket(name, location=region)
            return True
        except Exception as e:
            logger.error(f"GCS create_bucket error: {e}")
            return False

    def delete_bucket(self, name: str) -> bool:
        """Delete a bucket."""
        try:
            bucket = self.client.bucket(name)
            bucket.delete()
            return True
        except Exception as e:
            logger.error(f"GCS delete_bucket error: {e}")
            return False

    def bucket_exists(self, name: str) -> bool:
        """Check if a bucket exists."""
        try:
            self.client.get_bucket(name)
            return True
        except Exception as _exc:
            return False

    def upload_file(
        self, bucket: str, key: str, file_path: str, content_type: str | None = None
    ) -> bool:
        """Upload a file from local disk."""
        try:
            bucket_obj = self.client.bucket(bucket)
            blob = bucket_obj.blob(key)
            blob.upload_from_filename(file_path, content_type=content_type)
            return True
        except Exception as e:
            logger.error(f"GCS upload_file error: {e}")
            return False

    def download_file(self, bucket: str, key: str, file_path: str) -> bool:
        """Download a file to local disk."""
        try:
            bucket_obj = self.client.bucket(bucket)
            blob = bucket_obj.blob(key)
            blob.download_to_filename(file_path)
            return True
        except Exception as e:
            logger.error(f"GCS download_file error: {e}")
            return False

    def list_objects(self, bucket: str, prefix: str | None = None) -> list[str]:
        """List objects in a bucket."""
        try:
            blobs = self.client.list_blobs(bucket, prefix=prefix)
            return [blob.name for blob in blobs]
        except Exception as e:
            logger.error(f"GCS list_objects error: {e}")
            return []

    def delete_object(self, bucket: str, key: str) -> bool:
        """Delete an object."""
        try:
            bucket_obj = self.client.bucket(bucket)
            blob = bucket_obj.blob(key)
            blob.delete()
            return True
        except Exception as e:
            logger.error(f"GCS delete_object error: {e}")
            return False

    def get_object_metadata(self, bucket: str, key: str) -> dict[str, Any]:
        """Get object metadata."""
        try:
            bucket_obj = self.client.bucket(bucket)
            blob = bucket_obj.get_blob(key)
            return blob.metadata if blob and blob.metadata else {}
        except Exception as e:
            logger.error(f"GCS get_object_metadata error: {e}")
            return {}

    def generate_presigned_url(
        self,
        bucket: str,
        key: str,
        expires_in: int = 3600,
        operation: str = "get_object",
    ) -> str:
        """Generate a presigned URL."""
        import datetime

        try:
            bucket_obj = self.client.bucket(bucket)
            blob = bucket_obj.blob(key)
            # operation mapping for GCS
            method = "GET" if operation == "get_object" else "PUT"
            return blob.generate_signed_url(
                version="v4",
                expiration=datetime.timedelta(seconds=expires_in),
                method=method,
            )
        except Exception as e:
            logger.error(f"GCS generate_presigned_url error: {e}")
            return ""

    # Legacy methods for backward compatibility
    def upload_blob(
        self, bucket_name: str, source_file_name: str, destination_blob_name: str
    ) -> bool:
        return self.upload_file(bucket_name, destination_blob_name, source_file_name)

    def list_blobs(self, bucket_name: str) -> list[str]:
        return self.list_objects(bucket_name)

    def download_blob(
        self, bucket_name: str, source_blob_name: str, destination_file_name: str
    ) -> bool:
        return self.download_file(bucket_name, source_blob_name, destination_file_name)

    def get_metadata(self, bucket_name: str, blob_name: str) -> dict:
        return self.get_object_metadata(bucket_name, blob_name)

    def ensure_bucket(self, bucket_name: str, location: str = "US") -> bool:
        if self.bucket_exists(bucket_name):
            return True
        return self.create_bucket(bucket_name, region=location)
