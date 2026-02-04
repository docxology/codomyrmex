# Azure - Functional Specification

**Version**: v0.2.0 | **Status**: Active | **Last Updated**: February 2026

## Purpose

Provide Azure cloud service integrations for Blob Storage, VMs, and Azure Functions.

## AzureBlobClient Specification

### Constructor

```python
AzureBlobClient(account_url: Optional[str] = None)
```

- Falls back to `AZURE_STORAGE_ACCOUNT_URL` environment variable

### Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `upload_blob(container_name, blob_name, file_path)` | `bool` | Upload local file |
| `download_blob(container_name, blob_name, file_path)` | `bool` | Download to local |
| `list_blobs(container_name)` | `list[str]` | List blob names |
| `get_metadata(container_name, blob_name)` | `dict` | Get blob metadata |
| `ensure_container(container_name)` | `bool` | Create if not exists |

### Error Handling

- Returns `False` or empty list on failure
- Logs errors via `logging` module
- Client is `None` if account_url not provided

## Dependencies

| Package | Version | Required |
|---------|---------|----------|
| `azure-storage-blob` | >=12.0 | Yes |
| `azure-identity` | >=1.0 | Yes |

## Navigation

- **README**: [README.md](README.md)
- **Parent**: [cloud/](../README.md)
