# Personal AI Infrastructure - cloud/azure

**Module**: cloud/azure  
**Status**: Active

## Context

Azure integration using azure-storage-blob for Blob Storage operations.

## AI Agent Strategy

1. **Credential Check**: Verify `AzureBlobClient is not None` before use
2. **Account URL**: Required for client initialization
3. **Error Handling**: Client is `None` if misconfigured

## Key Patterns

```python
from codomyrmex.cloud import AzureBlobClient
import os

account_url = os.environ.get("AZURE_STORAGE_ACCOUNT_URL")
if account_url:
    client = AzureBlobClient(account_url=account_url)
    if client.client:  # Check internal client initialized
        client.upload_blob("container", "remote.txt", "local.txt")
```

## Navigation

- **Specification**: [SPEC.md](SPEC.md)
- **Parent**: [cloud/](../README.md)
