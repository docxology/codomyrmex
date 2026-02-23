# GCP Integration Module

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Google Cloud Platform integration providing Cloud Storage, with planned support for GCE compute and Cloud Functions.

## Components

| Component | Status | Description |
|-----------|--------|-------------|
| `GCSClient` | ✅ Active | Cloud Storage operations |
| `storage/` | Planned | Extended storage utilities |
| `compute/` | Planned | GCE instance management |
| `serverless/` | Planned | Cloud Functions management |

## Quick Start

```python
from codomyrmex.cloud.gcp import GCSClient

# Uses Application Default Credentials
client = GCSClient(project="my-project")

# Upload
client.upload_blob("my-bucket", "local.txt", "remote.txt")

# List
for blob in client.list_blobs("my-bucket"):
    print(blob)

# Download
client.download_blob("my-bucket", "remote.txt", "downloaded.txt")
```

## Authentication

Uses Google Application Default Credentials:

1. `GOOGLE_APPLICATION_CREDENTIALS` environment variable
2. gcloud CLI credentials
3. Service account on GCE/GKE/Cloud Run

## Dependencies

```bash
uv add google-cloud-storage
```

## Navigation

- **Parent**: [cloud/](../README.md)
- **Specification**: [SPEC.md](SPEC.md)
