"""
Infomaniak Object Storage Clients.

Provides both Swift (native OpenStack) and S3-compatible clients
for Infomaniak Public Cloud object storage.

Swift Endpoint: Available via openstacksdk
S3 Endpoints:
    - https://s3.pub1.infomaniak.cloud/
    - https://s3.pub2.infomaniak.cloud/
"""

from typing import Any

from codomyrmex.cloud.common import StorageClient
from codomyrmex.cloud.infomaniak.base import InfomaniakOpenStackBase, InfomaniakS3Base
from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


class InfomaniakObjectStorageClient(InfomaniakOpenStackBase):
    """
    Swift-based object storage client using OpenStack SDK.

    Provides native Swift API access for containers and objects.
    """

    _service_name = "object_storage"

    # =========================================================================
    # Container Operations
    # =========================================================================

    def list_containers(self) -> list[str]:
        """list all containers."""
        try:
            containers = list(self._conn.object_store.containers())
            return [c.name for c in containers]
        except Exception as e:
            logger.error("Failed to list containers: %s", e)
            return []

    def create_container(self, name: str) -> bool:
        """Create a container."""
        try:
            self._conn.object_store.create_container(name)
            logger.info("Created container: %s", name)
            return True
        except Exception as e:
            logger.error("Failed to create container %s: %s", name, e)
            return False

    def delete_container(self, name: str) -> bool:
        """Delete a container (must be empty)."""
        try:
            self._conn.object_store.delete_container(name)
            logger.info("Deleted container: %s", name)
            return True
        except Exception as e:
            logger.error("Failed to delete container %s: %s", name, e)
            return False

    def get_container_metadata(self, name: str) -> dict[str, Any]:
        """Get container metadata."""
        try:
            container = self._conn.object_store.get_container_metadata(name)
            return dict(container.metadata) if container else {}
        except Exception as e:
            logger.error("Failed to get container metadata %s: %s", name, e)
            return {}

    # =========================================================================
    # Object Operations
    # =========================================================================

    def list_objects(self, container: str, prefix: str | None = None) -> list[str]:
        """list objects in a container."""
        try:
            objects = list(self._conn.object_store.objects(container, prefix=prefix))
            return [obj.name for obj in objects]
        except Exception as e:
            logger.error("Failed to list objects in %s: %s", container, e)
            return []

    def upload_object(
        self, container: str, name: str, data: bytes, content_type: str | None = None
    ) -> bool:
        """Upload an object to a container."""
        try:
            self._conn.object_store.upload_object(
                container=container, name=name, data=data, content_type=content_type
            )
            logger.info("Uploaded object: %s/%s", container, name)
            return True
        except Exception as e:
            logger.error("Failed to upload object %s/%s: %s", container, name, e)
            return False

    def upload_file(
        self, container: str, name: str, file_path: str, content_type: str | None = None
    ) -> bool:
        """Upload a local file to a container."""
        try:
            with open(file_path, "rb") as f:
                data = f.read()
            return self.upload_object(container, name, data, content_type)
        except Exception as e:
            logger.error("Failed to upload file %s: %s", file_path, e)
            return False

    def download_object(self, container: str, name: str) -> bytes | None:
        """Download an object from a container."""
        try:
            obj = self._conn.object_store.download_object(container, name)
            return obj
        except Exception as e:
            logger.error("Failed to download object %s/%s: %s", container, name, e)
            return None

    def download_file(self, container: str, name: str, file_path: str) -> bool:
        """Download an object to a local file."""
        try:
            data = self.download_object(container, name)
            if data:
                with open(file_path, "wb") as f:
                    f.write(data)
                return True
            return False
        except Exception as e:
            logger.error("Failed to download file %s/%s: %s", container, name, e)
            return False

    def delete_object(self, container: str, name: str) -> bool:
        """Delete an object from a container."""
        try:
            self._conn.object_store.delete_object(name, container=container)
            logger.info("Deleted object: %s/%s", container, name)
            return True
        except Exception as e:
            logger.error("Failed to delete object %s/%s: %s", container, name, e)
            return False

    def get_object_metadata(self, container: str, name: str) -> dict[str, Any]:
        """Get object metadata."""
        try:
            obj = self._conn.object_store.get_object_metadata(name, container=container)
            return {
                "name": obj.name,
                "content_length": obj.content_length,
                "content_type": obj.content_type,
                "etag": obj.etag,
                "last_modified": str(obj.last_modified_at)
                if obj.last_modified_at
                else None,
            }
        except Exception as e:
            logger.error("Failed to get object metadata %s/%s: %s", container, name, e)
            return {}

    # =========================================================================
    # ACL Operations
    # =========================================================================

    def set_container_read_acl(self, container: str, acl: str) -> bool:
        """
        set container read ACL.

        Args:
            container: Container name
            acl: ACL string (e.g., ".r:*" for public read)
        """
        try:
            self._conn.object_store.set_container_metadata(container, read_acl=acl)
            logger.info("set read ACL for %s: %s", container, acl)
            return True
        except Exception as e:
            logger.error("Failed to set read ACL for %s: %s", container, e)
            return False

    def set_container_write_acl(self, container: str, acl: str) -> bool:
        """set container write ACL."""
        try:
            self._conn.object_store.set_container_metadata(container, write_acl=acl)
            logger.info("set write ACL for %s: %s", container, acl)
            return True
        except Exception as e:
            logger.error("Failed to set write ACL for %s: %s", container, e)
            return False


class InfomaniakS3Client(InfomaniakS3Base, StorageClient):
    """
    S3-compatible client for Infomaniak Object Storage.

    Uses boto3 with Infomaniak's S3 endpoint.

    Usage:
        from codomyrmex.cloud.infomaniak import InfomaniakS3Client

        s3 = InfomaniakS3Client.from_env()
        s3.upload_file("my-bucket", "key.txt", "local.txt")
    """

    # =========================================================================
    # Bucket Operations
    # =========================================================================

    def list_buckets(self) -> list[str]:
        """list all buckets."""
        try:
            response = self._client.list_buckets()
            return [b["Name"] for b in response.get("Buckets", [])]
        except Exception as e:
            logger.error("Failed to list buckets: %s", e)
            return []

    def create_bucket(self, name: str, region: str | None = None) -> bool:
        """Create a bucket."""
        try:
            kwargs = {"Bucket": name}
            if region:
                kwargs["CreateBucketConfiguration"] = {"LocationConstraint": region}
            self._client.create_bucket(**kwargs)
            logger.info("Created bucket: %s", name)
            return True
        except Exception as e:
            logger.error("Failed to create bucket %s: %s", name, e)
            return False

    def delete_bucket(self, name: str) -> bool:
        """Delete a bucket (must be empty)."""
        try:
            self._client.delete_bucket(Bucket=name)
            logger.info("Deleted bucket: %s", name)
            return True
        except Exception as e:
            logger.error("Failed to delete bucket %s: %s", name, e)
            return False

    def bucket_exists(self, name: str) -> bool:
        """Check if a bucket exists."""
        try:
            self._client.head_bucket(Bucket=name)
            return True
        except Exception as e:
            logger.warning("Bucket existence check failed for %r: %s", name, e)
            return False

    # =========================================================================
    # Object Operations
    # =========================================================================

    def list_objects(
        self, bucket: str, prefix: str | None = None, max_keys: int = 1000
    ) -> list[str]:
        """list objects in a bucket."""
        try:
            params = {"Bucket": bucket, "MaxKeys": max_keys}
            if prefix:
                params["Prefix"] = prefix

            response = self._client.list_objects_v2(**params)
            return [obj["Key"] for obj in response.get("Contents", [])]
        except Exception as e:
            logger.error("Failed to list objects in %s: %s", bucket, e)
            return []

    def upload_file(
        self, bucket: str, key: str, file_path: str, content_type: str | None = None
    ) -> bool:
        """Upload a local file to a bucket."""
        try:
            extra_args = {}
            if content_type:
                extra_args["ContentType"] = content_type
            self._client.upload_file(file_path, bucket, key, ExtraArgs=extra_args)
            logger.info("Uploaded file: %s/%s", bucket, key)
            return True
        except Exception as e:
            logger.error("Failed to upload file to %s/%s: %s", bucket, key, e)
            return False

    def upload_data(
        self, bucket: str, key: str, data: bytes, content_type: str | None = None
    ) -> bool:
        """Upload raw data to a bucket."""
        try:
            params: dict[str, Any] = {"Bucket": bucket, "Key": key, "Body": data}
            if content_type:
                params["ContentType"] = content_type

            self._client.put_object(**params)
            logger.info("Uploaded data: %s/%s", bucket, key)
            return True
        except Exception as e:
            logger.error("Failed to upload data to %s/%s: %s", bucket, key, e)
            return False

    def download_file(self, bucket: str, key: str, file_path: str) -> bool:
        """Download an object to a local file."""
        try:
            self._client.download_file(bucket, key, file_path)
            logger.info("Downloaded file: %s/%s", bucket, key)
            return True
        except Exception as e:
            logger.error("Failed to download %s/%s: %s", bucket, key, e)
            return False

    def download_data(self, bucket: str, key: str) -> bytes | None:
        """Download an object as bytes."""
        try:
            response = self._client.get_object(Bucket=bucket, Key=key)
            return response["Body"].read()
        except Exception as e:
            logger.error("Failed to download %s/%s: %s", bucket, key, e)
            return None

    def delete_object(self, bucket: str, key: str) -> bool:
        """Delete an object."""
        try:
            self._client.delete_object(Bucket=bucket, Key=key)
            logger.info("Deleted object: %s/%s", bucket, key)
            return True
        except Exception as e:
            logger.error("Failed to delete %s/%s: %s", bucket, key, e)
            return False

    def delete_file(self, bucket: str, key: str) -> bool:
        """Delete a file. ABC-compatible alias for delete_object."""
        return self.delete_object(bucket, key)

    def get_object_metadata(self, bucket: str, key: str) -> dict[str, Any]:
        """Get object metadata."""
        try:
            response = self._client.head_object(Bucket=bucket, Key=key)
            return response.get("Metadata", {})
        except Exception as e:
            logger.error("Failed to get metadata for %s/%s: %s", bucket, key, e)
            return {}

    def get_metadata(self, bucket: str, key: str) -> dict[str, Any]:
        """Legacy alias for get_object_metadata."""
        return self.get_object_metadata(bucket, key)

    def generate_presigned_url(
        self,
        bucket: str,
        key: str,
        expires_in: int = 3600,
        operation: str = "get_object",
    ) -> str:
        """
        Generate a presigned URL for temporary access.

        Args:
            bucket: Bucket name
            key: Object key
            expires_in: URL expiration in seconds
            operation: Operation type (e.g., "get_object", "put_object")
        """
        try:
            url = self._client.generate_presigned_url(
                ClientMethod=operation,
                Params={"Bucket": bucket, "Key": key},
                ExpiresIn=expires_in,
            )
            return url
        except Exception as e:
            logger.error("Failed to generate presigned URL: %s", e)
            return ""

    # =========================================================================
    # Advanced S3 Operations
    # =========================================================================

    def copy_object(
        self, src_bucket: str, src_key: str, dst_bucket: str, dst_key: str
    ) -> bool:
        """Copy an object between buckets or within a bucket."""
        try:
            self._client.copy_object(
                Bucket=dst_bucket,
                Key=dst_key,
                CopySource={"Bucket": src_bucket, "Key": src_key},
            )
            logger.info(
                "Copied %s/%s -> %s/%s", src_bucket, src_key, dst_bucket, dst_key
            )
            return True
        except Exception as e:
            logger.error("Failed to copy object: %s", e)
            return False

    def list_objects_paginated(
        self, bucket: str, prefix: str | None = None
    ) -> list[str]:
        """list all objects using pagination (handles >1000 objects)."""
        try:
            paginator = self._client.get_paginator("list_objects_v2")
            params: dict[str, Any] = {"Bucket": bucket}
            if prefix:
                params["Prefix"] = prefix

            keys: list[str] = []
            for page in paginator.paginate(**params):
                for obj in page.get("Contents", []):
                    keys.append(obj["Key"])
            return keys
        except Exception as e:
            logger.error("Failed to list objects (paginated) in %s: %s", bucket, e)
            return []

    def delete_objects_batch(self, bucket: str, keys: list[str]) -> dict[str, Any]:
        """
        Delete multiple objects in a single request.

        Auto-batches if more than 1000 keys (S3 limit per request).

        Returns:
            dict with 'deleted' count and 'errors' list
        """
        deleted_count = 0
        errors: list[dict[str, Any]] = []

        try:
            # Batch in groups of 1000
            for i in range(0, len(keys), 1000):
                batch = keys[i : i + 1000]
                response = self._client.delete_objects(
                    Bucket=bucket,
                    Delete={
                        "Objects": [{"Key": k} for k in batch],
                        "Quiet": False,
                    },
                )
                deleted_count += len(response.get("Deleted", []))
                errors.extend(response.get("Errors", []))

            logger.info("Batch deleted %s objects from %s", deleted_count, bucket)
        except Exception as e:
            logger.error("Failed batch delete in %s: %s", bucket, e)
            errors.append({"Key": "batch", "Message": str(e)})

        return {"deleted": deleted_count, "errors": errors}

    def enable_versioning(self, bucket: str) -> bool:
        """Enable versioning on a bucket."""
        try:
            self._client.put_bucket_versioning(
                Bucket=bucket, VersioningConfiguration={"Status": "Enabled"}
            )
            logger.info("Enabled versioning on bucket: %s", bucket)
            return True
        except Exception as e:
            logger.error("Failed to enable versioning on %s: %s", bucket, e)
            return False

    def get_versioning(self, bucket: str) -> str | None:
        """
        Get versioning status of a bucket.

        Returns:
            "Enabled", "Suspended", or None if never configured
        """
        try:
            response = self._client.get_bucket_versioning(Bucket=bucket)
            return response.get("Status")
        except Exception as e:
            logger.error("Failed to get versioning for %s: %s", bucket, e)
            return None

    def get_bucket_policy(self, bucket: str) -> str | None:
        """
        Get the bucket policy as a JSON string.

        Returns:
            JSON policy string or None if no policy set
        """
        try:
            response = self._client.get_bucket_policy(Bucket=bucket)
            return response.get("Policy")
        except Exception as e:
            error_str = str(e)
            if "NoSuchBucketPolicy" in error_str or "404" in error_str:
                return None
            logger.error("Failed to get bucket policy for %s: %s", bucket, e)
            return None

    def put_bucket_policy(self, bucket: str, policy: str) -> bool:
        """
        set the bucket policy.

        Args:
            bucket: Bucket name
            policy: JSON policy string
        """
        try:
            self._client.put_bucket_policy(Bucket=bucket, Policy=policy)
            logger.info("set bucket policy on: %s", bucket)
            return True
        except Exception as e:
            logger.error("Failed to set bucket policy on %s: %s", bucket, e)
            return False
