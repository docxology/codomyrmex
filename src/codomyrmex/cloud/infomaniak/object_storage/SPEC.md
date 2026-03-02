# Object Storage -- Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Provides dual-protocol object storage access for Infomaniak Public Cloud: native OpenStack Swift via `InfomaniakObjectStorageClient` and S3-compatible access via `InfomaniakS3Client` (boto3). Supports container/bucket lifecycle, object CRUD, ACLs, presigned URLs, batch operations, versioning, and bucket policies.

## Architecture

Two-class design. `InfomaniakObjectStorageClient` extends `InfomaniakOpenStackBase` for Swift operations via `self._conn.object_store.*`. `InfomaniakS3Client` extends `InfomaniakS3Base` (boto3 wrapper) and implements the `StorageClient` ABC. S3 endpoints are `https://s3.pub1.infomaniak.cloud/` and `https://s3.pub2.infomaniak.cloud/`.

## Key Methods -- Swift Client (`InfomaniakObjectStorageClient`)

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `list_containers` | (none) | `list[str]` | Container names |
| `create_container` | `name: str` | `bool` | Create container |
| `delete_container` | `name: str` | `bool` | Delete (must be empty) |
| `get_container_metadata` | `name: str` | `dict` | Container metadata |
| `list_objects` | `container, prefix` | `list[str]` | Object names |
| `upload_object` | `container, name, data: bytes, content_type` | `bool` | Upload bytes |
| `upload_file` | `container, name, file_path, content_type` | `bool` | Upload local file |
| `download_object` | `container, name` | `bytes or None` | Download bytes |
| `download_file` | `container, name, file_path` | `bool` | Download to file |
| `delete_object` | `container, name` | `bool` | Delete object |
| `get_object_metadata` | `container, name` | `dict` | Object metadata |
| `set_container_read_acl` | `container, acl` | `bool` | Set read ACL (e.g., ".r:*") |
| `set_container_write_acl` | `container, acl` | `bool` | Set write ACL |

## Key Methods -- S3 Client (`InfomaniakS3Client`)

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `list_buckets` | (none) | `list[str]` | Bucket names |
| `create_bucket` / `delete_bucket` | `name: str` | `bool` | Bucket lifecycle |
| `bucket_exists` | `name: str` | `bool` | HEAD bucket check |
| `list_objects` | `bucket, prefix, max_keys` | `list[str]` | Object keys (max 1000) |
| `list_objects_paginated` | `bucket, prefix` | `list[str]` | All keys via paginator |
| `upload_file` | `bucket, key, file_path, extra_args` | `bool` | Upload file |
| `upload_data` | `bucket, key, data: bytes, content_type` | `bool` | Upload bytes |
| `download_file` / `download_data` | `bucket, key, ...` | `bool / bytes` | Download |
| `delete_object` | `bucket, key` | `bool` | Delete object |
| `delete_objects_batch` | `bucket, keys: list[str]` | `dict` | Batch delete (auto-batches at 1000) |
| `get_metadata` | `bucket, key` | `dict` | HEAD object metadata |
| `generate_presigned_url` | `bucket, key, expires_in, http_method` | `str or None` | Presigned URL |
| `copy_object` | `src_bucket, src_key, dst_bucket, dst_key` | `bool` | Copy object |
| `enable_versioning` / `get_versioning` | `bucket: str` | `bool / str` | Versioning management |
| `get_bucket_policy` / `put_bucket_policy` | `bucket, policy` | `str or None / bool` | Policy JSON management |

## Dependencies

- **Internal**: `InfomaniakOpenStackBase`, `InfomaniakS3Base`, `codomyrmex.cloud.common.StorageClient`
- **External**: `openstacksdk` (Swift proxy), `boto3` (S3 client), `logging`

## Constraints

- `delete_objects_batch` auto-chunks in groups of 1000 per S3 API limit; returns `{"deleted": N, "errors": [...]}`.
- `get_bucket_policy` suppresses `NoSuchBucketPolicy` / HTTP 404 and returns `None` instead.
- `upload_file` (Swift) reads entire file into memory before uploading.
- `delete_file` (S3) is an alias for `delete_object` to satisfy `StorageClient` ABC.

## Error Handling

- All methods catch `Exception`, log via `logger.error`, and return sentinel values.
- `get_bucket_policy` additionally checks error strings for `NoSuchBucketPolicy` / `404` to avoid logging non-errors.
