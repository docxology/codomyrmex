# Codomyrmex Agents — src/codomyrmex/cloud

**Version**: v0.2.0 | **Status**: Active | **Last Updated**: February 2026

## Purpose

Cloud provider integration module supporting AWS, GCP, Azure, and Coda.io. Provides unified interfaces for cloud resources, storage, compute, and serverless services.

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
└── coda_io/             # Coda.io API
    ├── CodaClient       # REST API v1 client
    ├── models.py        # Data models (Doc, Page, Table, Row, etc.)
    └── exceptions.py    # API error types
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

## Operating Contracts

### Import Pattern

```python
# Recommended: Direct client imports
from codomyrmex.cloud import S3Client, GCSClient, AzureBlobClient, CodaClient

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

## Navigation Links

- **📁 Parent Directory**: [codomyrmex](../README.md)
- **🏠 Project Root**: [../../../README.md](../../../README.md)
- **📖 Specification**: [SPEC.md](SPEC.md)
- **🔌 API Reference**: [API_SPECIFICATION.md](API_SPECIFICATION.md)
