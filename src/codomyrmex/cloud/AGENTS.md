# Codomyrmex Agents — src/codomyrmex/cloud

**Version**: v1.1.0 | **Status**: Active | **Last Updated**: March 2026

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

## MCP Interface

This module exposes cloud operations for Model Context Protocol agents:

- `list_cloud_instances()`: Lists active compute instances (Infomaniak).
- `list_s3_buckets()`: Lists S3 buckets (Infomaniak).
- `upload_file_to_s3(file_path, bucket, object_name)`: Uploads to Infomaniak S3.

## PAI Agent Role Access Matrix

| PAI Agent | Access Level | Primary Capabilities | Trust Level |
|-----------|-------------|---------------------|-------------|
| **Engineer** | Full | `list_cloud_instances`, `list_s3_buckets`, `upload_file_to_s3`; lifecycle management | TRUSTED |
| **Architect** | Read + Design | Resource listing, inventory, architecture review | OBSERVED |
| **QATester** | Validation | Resource availability verification, upload success confirmation | OBSERVED |

## Navigation Links

- **📁 Parent Directory**: [codomyrmex](../README.md)
- **🏠 Project Root**: [../../../README.md](../../../README.md)
- **📖 Specification**: [SPEC.md](SPEC.md)
- **🔌 API Reference**: [API_SPECIFICATION.md](API_SPECIFICATION.md)
