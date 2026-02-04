# Codomyrmex Agents — cloud/azure

**Version**: v0.2.0 | **Status**: Active | **Last Updated**: February 2026

## Purpose

Azure service integrations including Blob Storage, VMs (planned), and Azure Functions (planned).

## Active Components

| Component | Type | Status |
|-----------|------|--------|
| `AzureBlobClient` | Class | Active |
| `storage/` | Module | Planned |
| `compute/` | Module | Planned |
| `serverless/` | Module | Planned |

## Operating Contracts

```python
from codomyrmex.cloud import AzureBlobClient

if AzureBlobClient is None:
    print("azure-storage-blob not installed")
else:
    client = AzureBlobClient(account_url="https://myaccount.blob.core.windows.net")
```

## Navigation

- **📁 Parent**: [cloud/](../README.md)
- **📖 Specification**: [SPEC.md](SPEC.md)
