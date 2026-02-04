# Azure Integration Module

**Version**: v0.2.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Microsoft Azure integration providing Blob Storage, with planned support for VMs and Azure Functions.

## Components

| Component | Status | Description |
|-----------|--------|-------------|
| `AzureBlobClient` | ✅ Active | Blob Storage operations |
| `storage/` | Planned | Extended storage utilities |
| `compute/` | Planned | VM management |
| `serverless/` | Planned | Azure Functions management |

## Quick Start

```python
from codomyrmex.cloud.azure import AzureBlobClient

# Uses DefaultAzureCredential
client = AzureBlobClient(account_url="https://myaccount.blob.core.windows.net")

# Upload
client.upload_blob("my-container", "remote.txt", "local.txt")

# List
for blob in client.list_blobs("my-container"):
    print(blob)

# Download
client.download_blob("my-container", "remote.txt", "downloaded.txt")
```

## Authentication

Uses DefaultAzureCredential chain:

1. Environment variables (`AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, `AZURE_CLIENT_SECRET`)
2. Managed Identity (on Azure VMs/App Service)
3. Azure CLI credentials
4. Visual Studio Code Azure extension

## Dependencies

```bash
pip install azure-storage-blob azure-identity
```

## Navigation

- **Parent**: [cloud/](../README.md)
- **Specification**: [SPEC.md](SPEC.md)
