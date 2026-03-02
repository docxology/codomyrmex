# Codomyrmex Agents -- src/codomyrmex/cloud/infomaniak/object_storage

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Provides object storage operations for Infomaniak Public Cloud via two clients: `InfomaniakObjectStorageClient` (native OpenStack Swift API) and `InfomaniakS3Client` (S3-compatible API via boto3). Supports container/bucket CRUD, object upload/download, ACL management (Swift), presigned URLs, batch delete, versioning, and bucket policies (S3).

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `client.py` | `InfomaniakObjectStorageClient` | Swift client extending `InfomaniakOpenStackBase`; `_service_name = "object_storage"` |
| `client.py` | `list_containers()` / `create_container()` / `delete_container()` | Swift container lifecycle |
| `client.py` | `get_container_metadata(name)` | Get container metadata dict |
| `client.py` | `list_objects(container, prefix)` / `upload_object()` / `upload_file()` | Swift object operations |
| `client.py` | `download_object()` / `download_file()` / `delete_object()` | Swift object retrieval and deletion |
| `client.py` | `get_object_metadata(container, name)` | Object metadata (size, type, etag, last_modified) |
| `client.py` | `set_container_read_acl()` / `set_container_write_acl()` | Swift ACL management |
| `client.py` | `InfomaniakS3Client` | S3 client extending `InfomaniakS3Base` and `StorageClient` ABC; uses boto3 |
| `client.py` | `list_buckets()` / `create_bucket()` / `delete_bucket()` / `bucket_exists()` | S3 bucket lifecycle |
| `client.py` | `list_objects()` / `upload_file()` / `upload_data()` | S3 object upload |
| `client.py` | `download_file()` / `download_data()` / `delete_object()` / `delete_file()` | S3 object retrieval and deletion |
| `client.py` | `get_metadata(bucket, key)` | S3 object metadata via HEAD |
| `client.py` | `generate_presigned_url(bucket, key, expires_in, http_method)` | Presigned URL generation (GET or PUT) |
| `client.py` | `copy_object(src_bucket, src_key, dst_bucket, dst_key)` | Cross-bucket or intra-bucket copy |
| `client.py` | `list_objects_paginated(bucket, prefix)` | Paginated listing for >1000 objects |
| `client.py` | `delete_objects_batch(bucket, keys)` | Batch delete with auto-batching at 1000 keys |
| `client.py` | `enable_versioning()` / `get_versioning()` | Bucket versioning management |
| `client.py` | `get_bucket_policy()` / `put_bucket_policy()` | Bucket policy JSON management |

## Operating Contracts

- Swift client uses `self._conn.object_store.*` (openstacksdk); S3 client uses `self._client` (boto3).
- S3 endpoints: `https://s3.pub1.infomaniak.cloud/` and `https://s3.pub2.infomaniak.cloud/`.
- `delete_objects_batch` auto-batches in groups of 1000 (S3 API limit per request).
- `list_objects_paginated` handles >1000 objects via boto3 paginator.
- `get_bucket_policy` returns `None` (not error) for `NoSuchBucketPolicy` / 404.
- `delete_file` is an ABC-compatible alias for `delete_object`.
- All errors are logged and methods return sentinel values rather than raising.

## Integration Points

- **Depends on**: `codomyrmex.cloud.infomaniak.base.InfomaniakOpenStackBase`, `codomyrmex.cloud.infomaniak.base.InfomaniakS3Base`, `codomyrmex.cloud.common.StorageClient`, `openstacksdk`, `boto3`
- **Used by**: `codomyrmex.cloud.infomaniak` (parent), metering client (object storage usage)

## Navigation

- **Parent**: [infomaniak](../AGENTS.md)
- **Root**: [../../../../../README.md](../../../../../README.md)
