"""AWS integration submodule."""

from typing import Any, Optional

import boto3
from botocore.exceptions import ClientError

from codomyrmex.cloud.common import StorageClient
from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


class S3Client(StorageClient):
    """Wrapper for AWS S3 operations."""

    def __init__(
        self, region_name: str | None = None, session: boto3.Session | None = None
    ):
        self.session = session or boto3.Session()
        self.client = self.session.client("s3", region_name=region_name)

    def list_buckets(self) -> list[str]:
        """list storage buckets."""
        try:
            response = self.client.list_buckets()
            return [bucket["Name"] for bucket in response.get("Buckets", [])]
        except ClientError as e:
            logger.error("S3 list_buckets error: %s", e)
            return []

    def create_bucket(self, name: str, region: str | None = None) -> bool:
        """Create a bucket."""
        try:
            if region:
                self.client.create_bucket(
                    Bucket=name,
                    CreateBucketConfiguration={"LocationConstraint": region},
                )
            else:
                self.client.create_bucket(Bucket=name)
            return True
        except ClientError as e:
            logger.error("S3 create_bucket error: %s", e)
            return False

    def delete_bucket(self, name: str) -> bool:
        """Delete a bucket."""
        try:
            self.client.delete_bucket(Bucket=name)
            return True
        except ClientError as e:
            logger.error("S3 delete_bucket error: %s", e)
            return False

    def bucket_exists(self, name: str) -> bool:
        """Check if a bucket exists."""
        try:
            self.client.head_bucket(Bucket=name)
            return True
        except ClientError:
            return False

    def upload_file(
        self, bucket: str, key: str, file_path: str, content_type: str | None = None
    ) -> bool:
        """Upload a file from local disk."""
        extra_args = {}
        if content_type:
            extra_args["ContentType"] = content_type

        try:
            self.client.upload_file(file_path, bucket, key, ExtraArgs=extra_args)
            return True
        except ClientError as e:
            logger.error("S3 upload_file error: %s", e)
            return False

    def download_file(self, bucket: str, key: str, file_path: str) -> bool:
        """Download a file to local disk."""
        try:
            self.client.download_file(bucket, key, file_path)
            return True
        except ClientError as e:
            logger.error("S3 download_file error: %s", e)
            return False

    def list_objects(self, bucket: str, prefix: str | None = None) -> list[str]:
        """list objects in a bucket."""
        kwargs = {"Bucket": bucket}
        if prefix:
            kwargs["Prefix"] = prefix

        try:
            response = self.client.list_objects_v2(**kwargs)
            return [obj["Key"] for obj in response.get("Contents", [])]
        except ClientError as e:
            logger.error("S3 list_objects error: %s", e)
            return []

    def delete_object(self, bucket: str, key: str) -> bool:
        """Delete an object."""
        try:
            self.client.delete_object(Bucket=bucket, Key=key)
            return True
        except ClientError as e:
            logger.error("S3 delete_object error: %s", e)
            return False

    def get_object_metadata(self, bucket: str, key: str) -> dict[str, Any]:
        """Get object metadata."""
        try:
            response = self.client.head_object(Bucket=bucket, Key=key)
            return response.get("Metadata", {})
        except ClientError as e:
            logger.error("S3 get_object_metadata error: %s", e)
            return {}

    def generate_presigned_url(
        self,
        bucket: str,
        key: str,
        expires_in: int = 3600,
        operation: str = "get_object",
    ) -> str:
        """Generate a presigned URL."""
        try:
            return self.client.generate_presigned_url(
                ClientMethod=operation,
                Params={"Bucket": bucket, "Key": key},
                ExpiresIn=expires_in,
            )
        except ClientError as e:
            logger.error("S3 generate_presigned_url error: %s", e)
            return ""

    # Legacy method for backward compatibility
    def ensure_bucket(self, bucket: str, region: str | None = None) -> bool:
        """Ensure an S3 bucket exists (legacy)."""
        if self.bucket_exists(bucket):
            return True
        return self.create_bucket(bucket, region)
