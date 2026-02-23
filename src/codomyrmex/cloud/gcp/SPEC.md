# GCP - Functional Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Purpose

Provide GCP cloud service integrations for Cloud Storage, GCE compute, and Cloud Functions.

## GCSClient Specification

### Constructor

```python
GCSClient(project: Optional[str] = None)
```

### Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `upload_blob(bucket_name, source_file_name, destination_blob_name)` | `bool` | Upload local file |
| `download_blob(bucket_name, source_blob_name, destination_file_name)` | `bool` | Download to local |
| `list_blobs(bucket_name)` | `list[str]` | List blob names |
| `get_metadata(bucket_name, blob_name)` | `dict` | Get blob metadata |
| `ensure_bucket(bucket_name, location="US")` | `bool` | Create if not exists |

### Error Handling

- Returns `False` on failure
- Logs errors via `logging` module
- Catches generic `Exception`

## Dependencies

| Package | Version | Required |
|---------|---------|----------|
| `google-cloud-storage` | >=2.0 | Yes |

## Navigation

- **README**: [README.md](README.md)
- **Parent**: [cloud/](../README.md)
