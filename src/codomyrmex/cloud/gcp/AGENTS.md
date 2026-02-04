# Codomyrmex Agents — cloud/gcp

**Version**: v0.2.0 | **Status**: Active | **Last Updated**: February 2026

## Purpose

GCP service integrations including Cloud Storage, GCE (planned), and Cloud Functions (planned).

## Active Components

| Component | Type | Status |
|-----------|------|--------|
| `GCSClient` | Class | Active |
| `storage/` | Module | Planned |
| `compute/` | Module | Planned |
| `serverless/` | Module | Planned |

## Operating Contracts

```python
from codomyrmex.cloud import GCSClient

if GCSClient is None:
    print("google-cloud-storage not installed")
else:
    client = GCSClient(project="my-project")
```

## Navigation

- **📁 Parent**: [cloud/](../README.md)
- **📖 Specification**: [SPEC.md](SPEC.md)
