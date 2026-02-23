# AWS - Functional Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Purpose

Provide AWS cloud service integrations for S3 storage, EC2 compute, and Lambda serverless.

## S3Client Specification

### Constructor

```python
S3Client(region_name: Optional[str] = None)
```

### Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `upload_file(file_path, bucket, object_name=None)` | `bool` | Upload local file |
| `download_file(bucket, object_name, file_path)` | `bool` | Download to local |
| `list_objects(bucket)` | `list[str]` | List object keys |
| `get_metadata(bucket, object_name)` | `dict` | Get object metadata |
| `ensure_bucket(bucket, region=None)` | `bool` | Create if not exists |

### Error Handling

- Returns `False` on failure
- Logs errors via `logging` module
- Catches `botocore.exceptions.ClientError`

## Dependencies

| Package | Version | Required |
|---------|---------|----------|
| `boto3` | >=1.26 | Yes |
| `botocore` | >=1.29 | Transitive |

## Navigation

- **README**: [README.md](README.md)
- **Parent**: [cloud/](../README.md)
