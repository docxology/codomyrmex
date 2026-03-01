"""
Unit tests for Infomaniak Object Storage clients.

Tests cover:
- InfomaniakObjectStorageClient (Swift / OpenStack)
- InfomaniakS3Client (S3-compatible / boto3)

Covers container/bucket CRUD, object upload/download/delete,
ACL operations, presigned URLs, batch deletes, versioning,
bucket policies, and error paths.

Total: ~28 tests across 2 test classes.
"""



from _stubs import Stub

from codomyrmex.cloud.infomaniak.object_storage.client import (
    InfomaniakObjectStorageClient,
    InfomaniakS3Client,
)

# =========================================================================
# Test InfomaniakObjectStorageClient (Swift)
# =========================================================================

class TestInfomaniakObjectStorageClient:
    """Tests for InfomaniakObjectStorageClient (Swift / OpenStack API)."""

    # ----- Container Operations -----

    def test_list_containers(self, mock_openstack_connection):
        """list_containers returns container names from object_store."""
        c1 = Stub()
        c1.name = "alpha"
        c2 = Stub()
        c2.name = "beta"
        mock_openstack_connection.object_store.containers.return_value = [c1, c2]

        client = InfomaniakObjectStorageClient(mock_openstack_connection)
        result = client.list_containers()

        assert result == ["alpha", "beta"]

    def test_list_containers_error_returns_empty(self, mock_openstack_connection):
        """list_containers returns [] when the backend raises."""
        mock_openstack_connection.object_store.containers.side_effect = Exception("timeout")

        client = InfomaniakObjectStorageClient(mock_openstack_connection)
        assert client.list_containers() == []

    def test_create_container(self, mock_openstack_connection):
        """create_container calls object_store.create_container and returns True."""
        client = InfomaniakObjectStorageClient(mock_openstack_connection)
        assert client.create_container("new-bucket") is True
        mock_openstack_connection.object_store.create_container.assert_called_once_with(
            "new-bucket"
        )

    def test_delete_container(self, mock_openstack_connection):
        """delete_container calls object_store.delete_container and returns True."""
        client = InfomaniakObjectStorageClient(mock_openstack_connection)
        assert client.delete_container("old-bucket") is True
        mock_openstack_connection.object_store.delete_container.assert_called_once_with(
            "old-bucket"
        )

    def test_get_container_metadata(self, mock_openstack_connection):
        """get_container_metadata returns dict from container.metadata."""
        mock_container = Stub()
        mock_container.metadata = {"X-Container-Read": ".r:*"}
        mock_openstack_connection.object_store.get_container_metadata.return_value = (
            mock_container
        )

        client = InfomaniakObjectStorageClient(mock_openstack_connection)
        result = client.get_container_metadata("my-container")

        assert result == {"X-Container-Read": ".r:*"}

    def test_get_container_metadata_error_returns_empty(self, mock_openstack_connection):
        """get_container_metadata returns {} on error."""
        mock_openstack_connection.object_store.get_container_metadata.side_effect = (
            Exception("not found")
        )

        client = InfomaniakObjectStorageClient(mock_openstack_connection)
        assert client.get_container_metadata("missing") == {}

    # ----- Object Operations -----

    def test_list_objects(self, mock_openstack_connection):
        """list_objects returns object names from a container."""
        obj1 = Stub()
        obj1.name = "file1.txt"
        obj2 = Stub()
        obj2.name = "dir/file2.txt"
        mock_openstack_connection.object_store.objects.return_value = [obj1, obj2]

        client = InfomaniakObjectStorageClient(mock_openstack_connection)
        result = client.list_objects("my-container", prefix="dir/")

        assert result == ["file1.txt", "dir/file2.txt"]
        mock_openstack_connection.object_store.objects.assert_called_once_with(
            "my-container", prefix="dir/"
        )

    def test_upload_object(self, mock_openstack_connection):
        """upload_object calls object_store.upload_object with correct params."""
        client = InfomaniakObjectStorageClient(mock_openstack_connection)
        result = client.upload_object(
            "bucket", "key.txt", b"data bytes", content_type="text/plain"
        )

        assert result is True
        mock_openstack_connection.object_store.upload_object.assert_called_once_with(
            container="bucket",
            name="key.txt",
            data=b"data bytes",
            content_type="text/plain",
        )

    def test_upload_file(self, mock_openstack_connection, tmp_path):
        """upload_file reads file from disk and delegates to upload_object."""
        client = InfomaniakObjectStorageClient(mock_openstack_connection)

        f = tmp_path / "doc.pdf"
        f.write_bytes(b"file contents")

        result = client.upload_file(
            "bucket", "doc.pdf", str(f), content_type="application/pdf"
        )

        assert result is True
        mock_openstack_connection.object_store.upload_object.assert_called_once_with(
            container="bucket",
            name="doc.pdf",
            data=b"file contents",
            content_type="application/pdf",
        )

    def test_upload_file_error_returns_false(self, mock_openstack_connection):
        """upload_file returns False when the file cannot be read."""
        client = InfomaniakObjectStorageClient(mock_openstack_connection)

        result = client.upload_file("bucket", "key", "/nonexistent_path_abc123")

        assert result is False

    def test_download_object(self, mock_openstack_connection):
        """download_object returns raw bytes from object_store."""
        mock_openstack_connection.object_store.download_object.return_value = b"hello swift"

        client = InfomaniakObjectStorageClient(mock_openstack_connection)
        data = client.download_object("bucket", "key.txt")

        assert data == b"hello swift"

    def test_download_file(self, mock_openstack_connection, tmp_path):
        """download_file writes downloaded bytes to disk."""
        mock_openstack_connection.object_store.download_object.return_value = b"bytes on disk"

        client = InfomaniakObjectStorageClient(mock_openstack_connection)

        out = tmp_path / "out.bin"
        result = client.download_file("bucket", "key.bin", str(out))

        assert result is True
        assert out.read_bytes() == b"bytes on disk"

    def test_download_file_no_data_returns_false(self, mock_openstack_connection):
        """download_file returns False when download_object returns None."""
        mock_openstack_connection.object_store.download_object.return_value = None

        client = InfomaniakObjectStorageClient(mock_openstack_connection)

        # download_object returns None internally, so download_file should return False
        result = client.download_file("bucket", "missing.txt", "/tmp/claude/out.txt")

        assert result is False

    def test_delete_object(self, mock_openstack_connection):
        """delete_object calls object_store.delete_object with correct kwargs."""
        client = InfomaniakObjectStorageClient(mock_openstack_connection)
        assert client.delete_object("bucket", "key.txt") is True

        mock_openstack_connection.object_store.delete_object.assert_called_once_with(
            "key.txt", container="bucket"
        )

    def test_get_object_metadata(self, mock_openstack_connection):
        """get_object_metadata returns structured metadata dict."""
        mock_obj = Stub()
        mock_obj.name = "file.txt"
        mock_obj.content_length = 1024
        mock_obj.content_type = "text/plain"
        mock_obj.etag = "abc123"
        mock_obj.last_modified_at = "2026-01-15T10:00:00Z"
        mock_openstack_connection.object_store.get_object_metadata.return_value = mock_obj

        client = InfomaniakObjectStorageClient(mock_openstack_connection)
        meta = client.get_object_metadata("bucket", "file.txt")

        assert meta["name"] == "file.txt"
        assert meta["content_length"] == 1024
        assert meta["content_type"] == "text/plain"
        assert meta["etag"] == "abc123"
        assert "2026-01-15" in meta["last_modified"]

    # ----- ACL Operations -----

    def test_set_container_read_acl(self, mock_openstack_connection):
        """set_container_read_acl sets read_acl via set_container_metadata."""
        client = InfomaniakObjectStorageClient(mock_openstack_connection)
        assert client.set_container_read_acl("public-bucket", ".r:*") is True

        mock_openstack_connection.object_store.set_container_metadata.assert_called_once_with(
            "public-bucket", read_acl=".r:*"
        )

    def test_set_container_write_acl(self, mock_openstack_connection):
        """set_container_write_acl sets write_acl via set_container_metadata."""
        client = InfomaniakObjectStorageClient(mock_openstack_connection)
        assert client.set_container_write_acl("shared-bucket", "project:writers") is True

        mock_openstack_connection.object_store.set_container_metadata.assert_called_once_with(
            "shared-bucket", write_acl="project:writers"
        )


# =========================================================================
# Test InfomaniakS3Client (S3-compatible)
# =========================================================================

class TestInfomaniakS3Client:
    """Tests for InfomaniakS3Client (S3-compatible / boto3)."""

    # ----- Bucket Operations -----

    def test_list_buckets(self, mock_s3_client):
        """list_buckets extracts names from S3 Buckets response."""
        mock_s3_client.list_buckets.return_value = {
            "Buckets": [{"Name": "b1"}, {"Name": "b2"}]
        }

        client = InfomaniakS3Client(mock_s3_client)
        assert client.list_buckets() == ["b1", "b2"]

    def test_create_bucket(self, mock_s3_client):
        """create_bucket calls S3 create_bucket and returns True."""
        client = InfomaniakS3Client(mock_s3_client)
        assert client.create_bucket("new-bucket") is True
        mock_s3_client.create_bucket.assert_called_once_with(Bucket="new-bucket")

    def test_delete_bucket(self, mock_s3_client):
        """delete_bucket calls S3 delete_bucket and returns True."""
        client = InfomaniakS3Client(mock_s3_client)
        assert client.delete_bucket("old-bucket") is True
        mock_s3_client.delete_bucket.assert_called_once_with(Bucket="old-bucket")

    def test_bucket_exists_true(self, mock_s3_client):
        """bucket_exists returns True when head_bucket succeeds."""
        mock_s3_client.head_bucket.return_value = {}

        client = InfomaniakS3Client(mock_s3_client)
        assert client.bucket_exists("existing") is True

    def test_bucket_exists_false(self, mock_s3_client):
        """bucket_exists returns False when head_bucket raises."""
        mock_s3_client.head_bucket.side_effect = Exception("404 Not Found")

        client = InfomaniakS3Client(mock_s3_client)
        assert client.bucket_exists("missing") is False

    # ----- Object Operations -----

    def test_list_objects(self, mock_s3_client):
        """list_objects extracts keys from S3 Contents response."""
        mock_s3_client.list_objects_v2.return_value = {
            "Contents": [{"Key": "k1"}, {"Key": "k2"}]
        }

        client = InfomaniakS3Client(mock_s3_client)
        result = client.list_objects("bucket", prefix="docs/")

        assert result == ["k1", "k2"]
        mock_s3_client.list_objects_v2.assert_called_once_with(
            Bucket="bucket", MaxKeys=1000, Prefix="docs/"
        )

    def test_upload_file(self, mock_s3_client):
        """upload_file delegates to S3 upload_file."""
        client = InfomaniakS3Client(mock_s3_client)
        result = client.upload_file("bucket", "key.txt", "/tmp/claude/file.txt")

        assert result is True
        mock_s3_client.upload_file.assert_called_once_with(
            "/tmp/claude/file.txt", "bucket", "key.txt", ExtraArgs=None
        )

    def test_upload_data(self, mock_s3_client):
        """upload_data calls S3 put_object with Body and optional ContentType."""
        client = InfomaniakS3Client(mock_s3_client)
        result = client.upload_data("bucket", "key.json", b'{"a":1}', content_type="application/json")

        assert result is True
        mock_s3_client.put_object.assert_called_once_with(
            Bucket="bucket", Key="key.json", Body=b'{"a":1}', ContentType="application/json"
        )

    def test_download_file(self, mock_s3_client):
        """download_file calls S3 download_file and returns True."""
        client = InfomaniakS3Client(mock_s3_client)
        result = client.download_file("bucket", "key.txt", "/tmp/claude/out.txt")

        assert result is True
        mock_s3_client.download_file.assert_called_once_with(
            "bucket", "key.txt", "/tmp/claude/out.txt"
        )

    def test_download_data(self, mock_s3_client):
        """download_data reads Body from S3 get_object response."""
        mock_body = Stub()
        mock_body.read.return_value = b"raw bytes"
        mock_s3_client.get_object.return_value = {"Body": mock_body}

        client = InfomaniakS3Client(mock_s3_client)
        data = client.download_data("bucket", "key.bin")

        assert data == b"raw bytes"

    def test_delete_object(self, mock_s3_client):
        """delete_object calls S3 delete_object."""
        client = InfomaniakS3Client(mock_s3_client)
        assert client.delete_object("bucket", "key.txt") is True
        mock_s3_client.delete_object.assert_called_once_with(Bucket="bucket", Key="key.txt")

    def test_delete_file_delegates_to_delete_object(self, mock_s3_client):
        """delete_file is an alias that delegates to delete_object."""
        client = InfomaniakS3Client(mock_s3_client)
        assert client.delete_file("bucket", "key.txt") is True
        mock_s3_client.delete_object.assert_called_once_with(Bucket="bucket", Key="key.txt")

    def test_get_metadata(self, mock_s3_client):
        """get_metadata returns structured metadata from head_object."""
        mock_s3_client.head_object.return_value = {
            "ContentLength": 2048,
            "ContentType": "image/png",
            "ETag": '"abc123"',
            "LastModified": "2026-01-20T12:00:00Z",
            "Metadata": {"custom-key": "custom-value"},
        }

        client = InfomaniakS3Client(mock_s3_client)
        meta = client.get_metadata("bucket", "photo.png")

        assert meta["content_length"] == 2048
        assert meta["content_type"] == "image/png"
        assert meta["etag"] == '"abc123"'
        assert meta["metadata"] == {"custom-key": "custom-value"}

    def test_generate_presigned_url_get(self, mock_s3_client):
        """generate_presigned_url with GET uses get_object ClientMethod."""
        mock_s3_client.generate_presigned_url.return_value = "https://s3.example.com/signed"

        client = InfomaniakS3Client(mock_s3_client)
        url = client.generate_presigned_url("bucket", "key.txt", expires_in=3600, http_method="GET")

        assert url == "https://s3.example.com/signed"
        mock_s3_client.generate_presigned_url.assert_called_once_with(
            ClientMethod="get_object",
            Params={"Bucket": "bucket", "Key": "key.txt"},
            ExpiresIn=3600,
        )

    def test_generate_presigned_url_put(self, mock_s3_client):
        """generate_presigned_url with PUT uses put_object ClientMethod."""
        mock_s3_client.generate_presigned_url.return_value = "https://s3.example.com/upload"

        client = InfomaniakS3Client(mock_s3_client)
        url = client.generate_presigned_url("bucket", "key.txt", http_method="PUT")

        assert url == "https://s3.example.com/upload"
        mock_s3_client.generate_presigned_url.assert_called_once_with(
            ClientMethod="put_object",
            Params={"Bucket": "bucket", "Key": "key.txt"},
            ExpiresIn=3600,
        )

    # ----- Advanced S3 Operations -----

    def test_copy_object(self, mock_s3_client):
        """copy_object calls S3 copy_object with CopySource dict."""
        client = InfomaniakS3Client(mock_s3_client)
        result = client.copy_object("src-bucket", "src-key", "dst-bucket", "dst-key")

        assert result is True
        mock_s3_client.copy_object.assert_called_once_with(
            Bucket="dst-bucket",
            Key="dst-key",
            CopySource={"Bucket": "src-bucket", "Key": "src-key"},
        )

    def test_list_objects_paginated(self, mock_s3_client):
        """list_objects_paginated uses paginator to collect all keys."""
        mock_paginator = Stub()
        mock_paginator.paginate.return_value = [
            {"Contents": [{"Key": "page1-k1"}, {"Key": "page1-k2"}]},
            {"Contents": [{"Key": "page2-k1"}]},
        ]
        mock_s3_client.get_paginator.return_value = mock_paginator

        client = InfomaniakS3Client(mock_s3_client)
        result = client.list_objects_paginated("bucket", prefix="data/")

        assert result == ["page1-k1", "page1-k2", "page2-k1"]
        mock_s3_client.get_paginator.assert_called_once_with("list_objects_v2")
        mock_paginator.paginate.assert_called_once_with(Bucket="bucket", Prefix="data/")

    def test_delete_objects_batch(self, mock_s3_client):
        """delete_objects_batch sends batch delete and returns deleted count and errors."""
        mock_s3_client.delete_objects.return_value = {
            "Deleted": [{"Key": "k1"}, {"Key": "k2"}],
            "Errors": [{"Key": "k3", "Message": "Access Denied"}],
        }

        client = InfomaniakS3Client(mock_s3_client)
        result = client.delete_objects_batch("bucket", ["k1", "k2", "k3"])

        assert result["deleted"] == 2
        assert len(result["errors"]) == 1
        assert result["errors"][0]["Key"] == "k3"

    def test_enable_versioning(self, mock_s3_client):
        """enable_versioning calls put_bucket_versioning with Enabled status."""
        client = InfomaniakS3Client(mock_s3_client)
        assert client.enable_versioning("bucket") is True

        mock_s3_client.put_bucket_versioning.assert_called_once_with(
            Bucket="bucket",
            VersioningConfiguration={"Status": "Enabled"},
        )

    def test_get_versioning(self, mock_s3_client):
        """get_versioning returns the Status string from the response."""
        mock_s3_client.get_bucket_versioning.return_value = {"Status": "Enabled"}

        client = InfomaniakS3Client(mock_s3_client)
        assert client.get_versioning("bucket") == "Enabled"

    def test_get_bucket_policy(self, mock_s3_client):
        """get_bucket_policy returns the policy JSON string."""
        mock_s3_client.get_bucket_policy.return_value = {
            "Policy": '{"Version":"2012-10-17","Statement":[]}'
        }

        client = InfomaniakS3Client(mock_s3_client)
        policy = client.get_bucket_policy("bucket")

        assert policy == '{"Version":"2012-10-17","Statement":[]}'

    def test_get_bucket_policy_no_policy_returns_none(self, mock_s3_client):
        """get_bucket_policy returns None for NoSuchBucketPolicy error."""
        mock_s3_client.get_bucket_policy.side_effect = Exception(
            "An error occurred (NoSuchBucketPolicy) when calling GetBucketPolicy"
        )

        client = InfomaniakS3Client(mock_s3_client)
        assert client.get_bucket_policy("bucket") is None

    def test_put_bucket_policy(self, mock_s3_client):
        """put_bucket_policy calls S3 put_bucket_policy with the JSON string."""
        policy_json = '{"Version":"2012-10-17","Statement":[]}'

        client = InfomaniakS3Client(mock_s3_client)
        assert client.put_bucket_policy("bucket", policy_json) is True

        mock_s3_client.put_bucket_policy.assert_called_once_with(
            Bucket="bucket", Policy=policy_json
        )


# =========================================================================

class TestInfomaniakSwiftClientExpanded:
    """Tests for InfomaniakObjectStorageClient (Swift) untested methods."""

    def _make_client(self):
        from codomyrmex.cloud.infomaniak.object_storage import (
            InfomaniakObjectStorageClient,
        )
        mock_conn = Stub()
        return InfomaniakObjectStorageClient(connection=mock_conn), mock_conn

    def test_delete_container(self):
        """Test functionality: delete container."""
        client, mc = self._make_client()
        assert client.delete_container("mybucket") is True
        mc.object_store.delete_container.assert_called_once_with("mybucket")

    def test_get_container_metadata(self):
        """Test functionality: get container metadata."""
        client, mc = self._make_client()
        meta = Stub()
        meta.metadata = {"x-count": "5"}
        mc.object_store.get_container_metadata.return_value = meta
        result = client.get_container_metadata("mybucket")
        assert isinstance(result, dict)

    def test_list_objects(self):
        """Test functionality: list objects."""
        client, mc = self._make_client()
        obj = Stub()
        obj.name = "file.txt"
        mc.object_store.objects.return_value = [obj]
        result = client.list_objects("mybucket")
        assert result == ["file.txt"]

    def test_list_objects_with_prefix(self):
        """Test functionality: list objects with prefix."""
        client, mc = self._make_client()
        mc.object_store.objects.return_value = []
        client.list_objects("mybucket", prefix="logs/")
        mc.object_store.objects.assert_called_once_with("mybucket", prefix="logs/")

    def test_get_object_metadata(self):
        """Test functionality: get object metadata."""
        client, mc = self._make_client()
        obj = Stub(content_length=1024,
                        content_type="text/plain", etag="abc",
                        last_modified_at=None)
        obj.name = "file.txt"
        mc.object_store.get_object_metadata.return_value = obj
        result = client.get_object_metadata("mybucket", "file.txt")
        assert result["name"] == "file.txt"
        assert result["content_length"] == 1024

    def test_set_container_read_acl(self):
        """Test functionality: set container read acl."""
        client, mc = self._make_client()
        assert client.set_container_read_acl("mybucket", ".r:*") is True
        mc.object_store.set_container_metadata.assert_called_once()

    def test_set_container_write_acl(self):
        """Test functionality: set container write acl."""
        client, mc = self._make_client()
        assert client.set_container_write_acl("mybucket", "user:admin") is True

    def test_list_containers_error(self):
        """Test functionality: list containers error."""
        client, mc = self._make_client()
        mc.object_store.containers.side_effect = Exception("fail")
        assert client.list_containers() == []


# =========================================================================
# ADDITIONAL S3 CLIENT TESTS
# =========================================================================


# =========================================================================

class TestInfomaniakS3ClientExpanded:
    """Tests for InfomaniakS3Client untested methods."""

    def _make_client(self):
        from codomyrmex.cloud.infomaniak.object_storage import InfomaniakS3Client
        mock_s3 = Stub()
        return InfomaniakS3Client(client=mock_s3), mock_s3

    def test_create_bucket(self):
        """Test functionality: create bucket."""
        client, s3 = self._make_client()
        assert client.create_bucket("mybucket") is True
        s3.create_bucket.assert_called_once_with(Bucket="mybucket")

    def test_delete_bucket(self):
        """Test functionality: delete bucket."""
        client, s3 = self._make_client()
        assert client.delete_bucket("mybucket") is True
        s3.delete_bucket.assert_called_once_with(Bucket="mybucket")

    def test_upload_file(self):
        """Test functionality: upload file."""
        client, s3 = self._make_client()
        assert client.upload_file("bkt", "key.txt", "/tmp/f.txt") is True
        s3.upload_file.assert_called_once_with("/tmp/f.txt", "bkt", "key.txt", ExtraArgs=None)

    def test_download_file(self):
        """Test functionality: download file."""
        client, s3 = self._make_client()
        assert client.download_file("bkt", "key.txt", "/tmp/out.txt") is True
        s3.download_file.assert_called_once_with("bkt", "key.txt", "/tmp/out.txt")

    def test_delete_file_delegates(self):
        """Test functionality: delete file delegates."""
        client, s3 = self._make_client()
        assert client.delete_file("bkt", "key.txt") is True
        s3.delete_object.assert_called_once_with(Bucket="bkt", Key="key.txt")

    def test_get_metadata(self):
        """Test functionality: get metadata."""
        client, s3 = self._make_client()
        s3.head_object.return_value = {
            "ContentLength": 100, "ContentType": "text/plain",
            "ETag": '"abc"', "LastModified": "2026-01-01",
            "Metadata": {}
        }
        result = client.get_metadata("bkt", "key.txt")
        assert result["content_length"] == 100
        assert result["content_type"] == "text/plain"

    def test_copy_object(self):
        """Test functionality: copy object."""
        client, s3 = self._make_client()
        assert client.copy_object("src", "sk", "dst", "dk") is True
        s3.copy_object.assert_called_once_with(
            Bucket="dst", Key="dk",
            CopySource={"Bucket": "src", "Key": "sk"}
        )

    def test_list_objects_paginated(self):
        """Test functionality: list objects paginated."""
        client, s3 = self._make_client()
        paginator = Stub()
        paginator.paginate.return_value = [
            {"Contents": [{"Key": "a.txt"}, {"Key": "b.txt"}]}
        ]
        s3.get_paginator.return_value = paginator
        result = client.list_objects_paginated("bkt")
        assert result == ["a.txt", "b.txt"]

    def test_delete_objects_batch(self):
        """Test functionality: delete objects batch."""
        client, s3 = self._make_client()
        s3.delete_objects.return_value = {
            "Deleted": [{"Key": "a.txt"}, {"Key": "b.txt"}],
            "Errors": []
        }
        result = client.delete_objects_batch("bkt", ["a.txt", "b.txt"])
        assert result["deleted"] == 2
        assert result["errors"] == []

    def test_enable_versioning(self):
        """Test functionality: enable versioning."""
        client, s3 = self._make_client()
        assert client.enable_versioning("bkt") is True
        s3.put_bucket_versioning.assert_called_once()

    def test_get_versioning(self):
        """Test functionality: get versioning."""
        client, s3 = self._make_client()
        s3.get_bucket_versioning.return_value = {"Status": "Enabled"}
        assert client.get_versioning("bkt") == "Enabled"

    def test_get_bucket_policy(self):
        """Test functionality: get bucket policy."""
        client, s3 = self._make_client()
        s3.get_bucket_policy.return_value = {"Policy": '{"Version":"2012"}'}
        assert client.get_bucket_policy("bkt") == '{"Version":"2012"}'

    def test_put_bucket_policy(self):
        """Test functionality: put bucket policy."""
        client, s3 = self._make_client()
        assert client.put_bucket_policy("bkt", '{"Version":"2012"}') is True
        s3.put_bucket_policy.assert_called_once()

    def test_list_buckets_error(self):
        """Test functionality: list buckets error."""
        client, s3 = self._make_client()
        s3.list_buckets.side_effect = Exception("fail")
        assert client.list_buckets() == []


# =========================================================================
# ADDITIONAL IDENTITY CLIENT TESTS
# =========================================================================
