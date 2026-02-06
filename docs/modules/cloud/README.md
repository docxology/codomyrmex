# Cloud Module Documentation

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Multi-cloud integration with AWS, GCP, Azure, and other cloud providers.

## Key Features

- **Multi-Cloud** — Unified API across providers
- **Storage** — S3, GCS, Azure Blob
- **Compute** — VM management
- **Serverless** — Lambda, Cloud Functions

## Quick Start

```python
from codomyrmex.cloud import CloudStorage, Provider

storage = CloudStorage(provider=Provider.AWS)
storage.upload("data.json", bucket="my-bucket")
content = storage.download("my-bucket", "data.json")
```

## Directory Contents

| File | Description |
|------|-------------|
| `README.md` | This file |
| `SPEC.md` | Technical specification |

## Navigation

- **Source**: [src/codomyrmex/cloud/](../../../src/codomyrmex/cloud/)
- **Parent**: [Modules](../README.md)
