# Codomyrmex Agents — src/codomyrmex/cloud

**Version**: v1.0.5 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Cloud provider integration module supporting AWS, GCP, Azure, Coda.io, and Infomaniak. Provides unified interfaces for cloud resources, storage, compute, serverless, DNS, orchestration, metering, and newsletter services.

## Module Architecture

```
cloud/
├── __init__.py          # Public API exports
├── common/              # Abstract base classes and utilities
│   ├── CloudClient      # Generic cloud resource management
│   ├── StorageClient    # Object storage abstraction
│   ├── ComputeClient    # VM/instance abstraction
│   └── ServerlessClient # Function-as-a-service abstraction
├── aws/                 # Amazon Web Services
│   ├── S3Client         # S3 object storage
│   ├── storage/         # Extended storage operations
│   ├── compute/         # EC2 operations (planned)
│   └── serverless/      # Lambda operations (planned)
├── gcp/                 # Google Cloud Platform
│   ├── GCSClient        # Cloud Storage
│   ├── storage/         # Extended storage operations
│   ├── compute/         # GCE operations (planned)
│   └── serverless/      # Cloud Functions (planned)
├── azure/               # Microsoft Azure
│   ├── AzureBlobClient  # Blob Storage
│   ├── storage/         # Extended storage operations
│   ├── compute/         # VM operations (planned)
│   └── serverless/      # Azure Functions (planned)
├── coda_io/             # Coda.io API
│   ├── CodaClient       # REST API v1 client
│   ├── models.py        # Data models (Doc, Page, Table, Row, etc.)
│   └── exceptions.py    # API error types
└── infomaniak/          # Infomaniak Public Cloud + Newsletter
    ├── auth.py          # Credentials and connection factories
    ├── compute/         # InfomaniakComputeClient (Nova)
    ├── block_storage/   # InfomaniakVolumeClient (Cinder)
    ├── network/         # InfomaniakNetworkClient (Neutron/Octavia)
    ├── object_storage/  # InfomaniakObjectStorageClient (Swift) / InfomaniakS3Client
    ├── identity/        # InfomaniakIdentityClient (Keystone)
    ├── dns/             # InfomaniakDNSClient (Designate)
    ├── orchestration/   # InfomaniakHeatClient (Heat)
    ├── metering/        # InfomaniakMeteringClient
    └── newsletter/      # InfomaniakNewsletterClient (REST API)
```

## Active Components

| Component | Type | Status | Description |
|-----------|------|--------|-------------|
| `S3Client` | Class | Active | AWS S3 object storage client |
| `GCSClient` | Class | Active | GCP Cloud Storage client |
| `AzureBlobClient` | Class | Active | Azure Blob Storage client |
| `CodaClient` | Class | Active | Coda.io REST API v1 client |
| `StorageClient` | ABC | Active | Abstract storage interface |
| `ComputeClient` | ABC | Planned | Abstract compute interface |
| `ServerlessClient` | ABC | Planned | Abstract serverless interface |
| `InfomaniakComputeClient` | Class | Active | Infomaniak compute (Nova) |
| `InfomaniakVolumeClient` | Class | Active | Infomaniak block storage (Cinder) |
| `InfomaniakNetworkClient` | Class | Active | Infomaniak networking (Neutron/Octavia) |
| `InfomaniakObjectStorageClient` | Class | Active | Infomaniak Swift object storage |
| `InfomaniakS3Client` | Class | Active | Infomaniak S3-compatible storage |
| `InfomaniakIdentityClient` | Class | Active | Infomaniak identity (Keystone) |
| `InfomaniakDNSClient` | Class | Active | Infomaniak DNS (Designate) |
| `InfomaniakHeatClient` | Class | Active | Infomaniak orchestration (Heat) |
| `InfomaniakMeteringClient` | Class | Active | Infomaniak metering/billing |
| `InfomaniakNewsletterClient` | Class | Active | Infomaniak Newsletter REST API |

## Operating Contracts

### Import Pattern

```python
# Recommended: Direct client imports
from codomyrmex.cloud import S3Client, GCSClient, AzureBlobClient, CodaClient

# Infomaniak clients
from codomyrmex.cloud import InfomaniakComputeClient, InfomaniakS3Client
from codomyrmex.cloud.infomaniak.newsletter import InfomaniakNewsletterClient

# Access common abstractions
from codomyrmex.cloud.common import StorageClient, CloudProvider
```

### Error Handling Pattern

```python
from codomyrmex.cloud import S3Client
import logging

logger = logging.getLogger(__name__)

client = S3Client()
try:
    objects = client.list_objects("my-bucket")
except Exception as e:
    logger.error(f"Operation failed: {e}")
    # Errors are logged internally; re-raise or handle as needed
```

### Dependency Checks

```python
from codomyrmex.cloud import S3Client, GCSClient, AzureBlobClient

# Clients are None if optional dependencies are missing
if S3Client is None:
    print("boto3 not installed - AWS features unavailable")

if GCSClient is None:
    print("google-cloud-storage not installed - GCP features unavailable")

if AzureBlobClient is None:
    print("azure-storage-blob not installed - Azure features unavailable")

if InfomaniakComputeClient is None:
    print("openstacksdk not installed - Infomaniak features unavailable")
```

## Agent Integration Guidelines

1. **Use Public API**: Import from `codomyrmex.cloud`, not internal modules
2. **Check Availability**: Always verify client is not None before use
3. **Handle Errors**: All operations may raise exceptions; wrap in try/except
4. **Respect Rate Limits**: Coda.io has strict rate limits (see SPEC.md)
5. **Use Logging**: Errors are logged via `logging_monitoring` module

## Cross-Module Dependencies

| Module | Relationship |
|--------|--------------|
| `logging_monitoring` | Used for structured logging |
| `config_management` | Credential configuration |
| `validation` | Input validation |

## MCP Interface

This module exposes cloud operations for Model Context Protocol agents:

- Storage CRUD operations across providers
- Document management via Coda.io
- Resource listing and metadata retrieval

## PAI Agent Role Access Matrix

| PAI Agent | Access Level | Primary Capabilities | Trust Level |
|-----------|-------------|---------------------|-------------|
| **Engineer** | Full | `list_cloud_instances`, `list_s3_buckets`, `upload_file_to_s3`; full cloud lifecycle | TRUSTED |
| **Architect** | Read + Design | `list_cloud_instances`, `list_s3_buckets`; infrastructure inventory, cloud architecture review | OBSERVED |
| **QATester** | Validation | `list_cloud_instances`, `list_s3_buckets`; resource availability verification | OBSERVED |

### Engineer Agent
**Use Cases**: Deploying artifacts to S3 during EXECUTE, listing cloud instances for infrastructure awareness, managing cloud resource lifecycle.

### Architect Agent
**Use Cases**: Cloud infrastructure inventory during OBSERVE, reviewing instance configurations, planning cloud architecture.

### QATester Agent
**Use Cases**: Verifying cloud resource availability during VERIFY, confirming S3 upload success.

## Navigation Links

- **📁 Parent Directory**: [codomyrmex](../README.md)
- **🏠 Project Root**: [../../../README.md](../../../README.md)
- **📖 Specification**: [SPEC.md](SPEC.md)
- **🔌 API Reference**: [API_SPECIFICATION.md](API_SPECIFICATION.md)
