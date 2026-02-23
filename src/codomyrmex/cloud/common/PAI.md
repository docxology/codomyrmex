# Personal AI Infrastructure - cloud/common

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

**Module**: cloud/common  
**Status**: Active

## Context

Abstract base classes and utilities for cloud provider implementations. Use these interfaces when implementing provider-agnostic cloud operations.

## AI Agent Strategy

### 1. Provider Detection

```python
from codomyrmex.cloud.common import CloudConfig, CloudProvider

config = CloudConfig.from_env()
available_providers = [
    p for p in CloudProvider 
    if config.has_provider(p)
]
```

### 2. Interface-Based Programming

```python
from codomyrmex.cloud.common import StorageClient

def upload_data(client: StorageClient, bucket: str, key: str, data: bytes):
    """Works with any StorageClient implementation."""
    return client.upload_file(bucket, key, data)
```

### 3. Resource Management

```python
from codomyrmex.cloud.common import CloudResource, ResourceType

def filter_storage_resources(resources: list[CloudResource]):
    return [r for r in resources if r.resource_type == ResourceType.STORAGE]
```

## Key Interfaces

| ABC | When to Use |
|-----|-------------|
| `StorageClient` | File/object upload, download, listing |
| `ComputeClient` | VM lifecycle management |
| `ServerlessClient` | Function deployment and invocation |
| `CloudClient` | Generic resource CRUD operations |

## Best Practices

1. **Program to Interfaces**: Use ABCs as type hints
2. **Lazy Initialization**: Don't create clients until needed
3. **Credential Safety**: Use `CloudConfig.from_env()` instead of hardcoding

## Navigation

- **Specification**: [SPEC.md](SPEC.md)
- **Parent**: [cloud/](../README.md)
