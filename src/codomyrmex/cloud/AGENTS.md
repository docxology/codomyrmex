# Codomyrmex Agents — src/codomyrmex/cloud

**Version**: v1.1.4 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Unified cloud provider integration module for AWS, GCP, Azure, Coda.io, and Infomaniak. Provides consistent interfaces for object storage, compute, and document management.

## Module Architecture

```
cloud/
├── __init__.py          # Unified Public API exports
├── common/              # ABCs and shared models
│   ├── StorageClient    # Unified storage interface (S3, GCS, Blob)
│   ├── ComputeClient    # Unified compute interface
│   ├── CloudClient      # General resource management
│   └── CloudConfig      # Centralized credential loading
├── aws/                 # Amazon Web Services (S3Client)
├── gcp/                 # Google Cloud Platform (GCSClient)
├── azure/               # Microsoft Azure (AzureBlobClient)
├── coda_io/             # Coda.io (CodaClient)
└── infomaniak/          # Infomaniak (OpenStack and S3 clients)
```

## Core Interfaces

### StorageClient (AWS, GCP, Azure, Infomaniak S3)

All storage clients implement these methods:

- `list_buckets()`
- `create_bucket(name, region=None)`
- `delete_bucket(name)`
- `bucket_exists(name)`
- `upload_file(bucket, key, file_path, content_type=None)`
- `download_file(bucket, key, file_path)`
- `list_objects(bucket, prefix=None)`
- `delete_object(bucket, key)`
- `get_object_metadata(bucket, key)`
- `generate_presigned_url(bucket, key, expires_in=3600, operation="get_object")`

### CloudClient (Coda.io, Infomaniak)

Standardized resource operations:

- `list_resources(resource_type=None)`
- `get_resource(resource_id)`
- `create_resource(name, resource_type, config)`
- `delete_resource(resource_id)`

## Operating Contracts

### Unified Initialization

```python
from codomyrmex.cloud.common import CloudConfig, CloudProvider
from codomyrmex.cloud import S3Client, CodaClient

# 1. From environment variables
config = CloudConfig.from_env()

# 2. Check and initialize
if config.has_provider(CloudProvider.AWS):
    s3 = S3Client()  # Uses boto3 defaults or config

if config.has_provider(CloudProvider.CODA):
    creds = config.get_credentials(CloudProvider.CODA)
    coda = CodaClient(api_token=creds.access_key)
```

### Consistent Storage Usage

```python
def sync_config(storage: StorageClient, bucket: str, local_path: str):
    """Sync a file using any StorageClient (AWS, GCP, Azure)."""
    if storage.bucket_exists(bucket):
        storage.upload_file(bucket, "config.json", local_path)
```

## Agent Integration Guidelines

1. **Prefer ABCs**: Use `StorageClient` as a type hint for functions that work across providers.
2. **Verify Dependencies**: Check if provider clients are available (not None) before use.
3. **Use CloudConfig**: Leverage `CloudConfig.from_env()` to discover configured providers.
4. **Structured Logging**: Errors are logged automatically; use `CloudError` to catch unified exceptions.

## MCP Tools Available

| Tool | Description | Trust Level |
|------|-------------|-------------|
| `list_cloud_instances` | List active compute instances (Infomaniak) | SAFE |
| `list_s3_buckets` | List S3 buckets (Infomaniak) | SAFE |
| `upload_file_to_s3` | Upload a file to Infomaniak S3 | TRUSTED |

## PAI Agent Role Access Matrix

| PAI Agent | Access Level | MCP Tools | Trust Level |
|-----------|-------------|-----------|-------------|
| **Engineer** | Full | `list_cloud_instances`, `list_s3_buckets`, `upload_file_to_s3` | TRUSTED |
| **Architect** | Read + Design | `list_cloud_instances`, `list_s3_buckets` — resource inventory and architecture review | OBSERVED |
| **QATester** | Validation | `list_cloud_instances`, `list_s3_buckets` — resource availability verification | OBSERVED |
| **Researcher** | Read-only | `list_cloud_instances`, `list_s3_buckets` — inspect cloud resource state | SAFE |

### Engineer Agent
**Use Cases**: Listing and managing cloud resources during EXECUTE, uploading artifacts to S3, infrastructure lifecycle management.

### Architect Agent
**Use Cases**: Resource inventory for architectural decisions, reviewing multi-cloud provider topology.

### QATester Agent
**Use Cases**: Verifying resource availability during VERIFY, confirming upload success.

### Researcher Agent
**Use Cases**: Inspecting cloud resource state and instance inventory for analysis.

## Navigation Links

- **📁 Parent Directory**: [codomyrmex](../README.md)
- **🏠 Project Root**: [../../../README.md](../../../README.md)
- **📖 Specification**: [SPEC.md](SPEC.md)
- **🔌 API Reference**: [API_SPECIFICATION.md](API_SPECIFICATION.md)


## Rule Reference

This module is governed by the following rule file:

- [`src/codomyrmex/agentic_memory/rules/modules/cloud.cursorrules`](src/codomyrmex/agentic_memory/rules/modules/cloud.cursorrules)
