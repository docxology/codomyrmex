# Personal AI Infrastructure - cloud/gcp

**Module**: cloud/gcp  
**Status**: Active

## Context

GCP integration using google-cloud-storage for Cloud Storage operations.

## AI Agent Strategy

1. **Credential Check**: Verify `GCSClient is not None` before use
2. **Project Selection**: Pass `project` for multi-project environments
3. **Error Handling**: All methods return `False` on failure

## Key Patterns

```python
from codomyrmex.cloud import GCSClient

client = GCSClient(project="my-project")

if client.upload_blob("bucket", "local.csv", "remote.csv"):
    print("Upload successful")
```

## Navigation

- **Specification**: [SPEC.md](SPEC.md)
- **Parent**: [cloud/](../README.md)
