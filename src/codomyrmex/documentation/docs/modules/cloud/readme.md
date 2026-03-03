# Cloud

**Version**: v1.0.8 | **Status**: Active | **Last Updated**: March 2026

## Overview

The Cloud module provides integrations with multiple cloud service APIs: Coda.io (document/database API), AWS (S3), GCP (Google Cloud Storage), Azure (Blob Storage), and Infomaniak (OpenStack-based compute, storage, network, DNS). The Coda.io client is always available; other providers require optional SDK dependencies (boto3, google-cloud-storage, azure-storage-blob, openstacksdk).

## Architecture Overview

```
cloud/
├── __init__.py              # Unified API with lazy-loaded providers
├── mcp_tools.py             # MCP tools (list_cloud_instances, list_s3_buckets, upload_file_to_s3)
├── common/                  # Shared cloud utilities
├── coda_io/                 # Coda.io REST API v1 client (always available)
├── aws/                     # AWS S3 client (requires boto3)
├── gcp/                     # GCP Storage client (requires google-cloud-storage)
├── azure/                   # Azure Blob client (requires azure-storage-blob)
└── infomaniak/              # Infomaniak OpenStack clients (requires openstacksdk)
```

## Key Classes and Functions

**`CodaClient`** -- Full Coda.io REST API v1 client for documents, tables, rows, formulas.

**`S3Client`** / **`GCSClient`** / **`AzureBlobClient`** -- Cloud storage clients (lazy-loaded).

**Infomaniak clients** -- Compute, Volume, Network, Object Storage, S3, Identity, DNS, Heat, Metering, Newsletter.

## MCP Tools Reference

| Tool | Description | Parameters | Trust Level |
|------|-------------|------------|-------------|
| `list_cloud_instances` | List cloud compute instances | (varies) | Safe |
| `list_s3_buckets` | List S3 buckets | (varies) | Safe |
| `upload_file_to_s3` | Upload a file to S3 | `bucket: str`, `key: str`, `path: str` | Destructive |

## Configuration

```bash
export CODA_API_TOKEN="your-coda-token"
export AWS_ACCESS_KEY_ID="..."
export AWS_SECRET_ACCESS_KEY="..."
```

## Related Modules

- [`containerization`](../containerization/readme.md) -- Container management on cloud infrastructure
- [`deployment`](../deployment/readme.md) -- Deployment to cloud environments

## Navigation

- **Source**: [src/codomyrmex/cloud/](../../../../src/codomyrmex/cloud/)
- **Parent**: [All Modules](../README.md)
