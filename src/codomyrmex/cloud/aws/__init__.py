"""AWS integration submodule."""

import logging
from typing import Any, Dict, Optional

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)

class S3Client:
    """Wrapper for AWS S3 operations."""

    def __init__(self, region_name: str | None = None):
        """Initialize this instance."""
        self.client = boto3.client('s3', region_name=region_name)

    def upload_file(self, file_path: str, bucket: str, object_name: str | None = None) -> bool:
        """Upload a file to an S3 bucket."""
        if object_name is None:
            object_name = file_path

        try:
            self.client.upload_file(file_path, bucket, object_name)
            return True
        except ClientError as e:
            logger.error(f"S3 upload error: {e}")
            return False

    def list_objects(self, bucket: str) -> list[str]:
        """List objects in an S3 bucket."""
        try:
            response = self.client.list_objects_v2(Bucket=bucket)
            return [obj['Key'] for obj in response.get('Contents', [])]
        except ClientError as e:
            logger.error(f"S3 list error: {e}")
            return []

    def download_file(self, bucket: str, object_name: str, file_path: str) -> bool:
        """Download an object from an S3 bucket."""
        try:
            self.client.download_file(bucket, object_name, file_path)
            return True
        except ClientError as e:
            logger.error(f"S3 download error: {e}")
            return False

    def get_metadata(self, bucket: str, object_name: str) -> dict[str, Any]:
        """Get object metadata."""
        try:
            response = self.client.head_object(Bucket=bucket, Key=object_name)
            return response.get('Metadata', {})
        except ClientError as e:
            logger.error(f"S3 metadata error: {e}")
            return {}

    def ensure_bucket(self, bucket: str, region: str | None = None) -> bool:
        """Ensure an S3 bucket exists."""
        try:
            self.client.head_bucket(Bucket=bucket)
            return True
        except ClientError:
            try:
                if region:
                    self.client.create_bucket(Bucket=bucket, CreateBucketConfiguration={'LocationConstraint': region})
                else:
                    self.client.create_bucket(Bucket=bucket)
                return True
            except ClientError as e:
                logger.error(f"S3 bucket creation error: {e}")
                return False
