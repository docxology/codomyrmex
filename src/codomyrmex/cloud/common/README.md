# Cloud Common Module

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The `common` submodule provides shared abstractions and utilities for cloud provider implementations. It defines abstract base classes (ABCs) that ensure consistent interfaces across AWS, GCP, and Azure.

## Key Components

### Enums

| Enum | Values | Description |
|------|--------|-------------|
| `CloudProvider` | `AWS`, `GCP`, `AZURE`, `LOCAL` | Supported cloud platforms |
| `ResourceType` | `COMPUTE`, `STORAGE`, `DATABASE`, `NETWORK`, `SERVERLESS`, `CONTAINER`, `QUEUE` | Cloud resource categories |

### Data Classes

| Class | Purpose |
|-------|---------|
| `CloudCredentials` | Provider credentials and configuration |
| `CloudResource` | Generic cloud resource representation |

### Abstract Base Classes

| ABC | Purpose | Key Methods |
|-----|---------|-------------|
| `CloudClient` | Generic resource management | `list_resources`, `get_resource`, `create_resource`, `delete_resource` |
| `StorageClient` | Object storage operations | `list_buckets`, `upload_file`, `download_file`, `delete_file`, `generate_presigned_url` |
| `ComputeClient` | VM/Instance management | `list_instances`, `start_instance`, `stop_instance`, `create_instance` |
| `ServerlessClient` | Function-as-a-Service | `list_functions`, `invoke_function`, `create_function`, `delete_function` |

### Configuration

| Class | Purpose |
|-------|---------|
| `CloudConfig` | Multi-provider credential management with environment variable loading |

## Usage Examples

### Creating Custom Storage Client

```python
from codomyrmex.cloud.common import StorageClient, CloudCredentials, CloudProvider
from typing import List, Optional

class MyStorageClient(StorageClient):
    def __init__(self, credentials: CloudCredentials):
        self.credentials = credentials
    
    def list_buckets(self) -> List[str]:
        # Implementation
        return ["bucket1", "bucket2"]
    
    def upload_file(self, bucket: str, key: str, data: bytes, 
                    content_type: Optional[str] = None) -> str:
        # Implementation
        return f"{bucket}/{key}"
    
    # ... other required methods
```

### Using CloudConfig

```python
from codomyrmex.cloud.common import CloudConfig, CloudProvider

# Load from environment variables
config = CloudConfig.from_env()

# Check provider availability
if config.has_provider(CloudProvider.AWS):
    creds = config.get_credentials(CloudProvider.AWS)
    print(f"AWS region: {creds.region}")
```

## Directory Contents

| File | Description |
|------|-------------|
| `__init__.py` | Module exports (ABCs, enums, dataclasses) |
| `README.md` | This documentation |
| `SPEC.md` | Interface specifications |
| `AGENTS.md` | Agent integration guide |
| `PAI.md` | AI infrastructure context |
| `py.typed` | PEP 561 typing marker |

## Navigation

- **Parent**: [cloud/](../README.md)
- **Specification**: [SPEC.md](SPEC.md)
- **Project Root**: [../../../../README.md](../../../../README.md)
