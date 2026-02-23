# Codomyrmex Agents — cloud/common

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Purpose

Shared abstractions and utilities for cloud provider implementations. Defines contracts that ensure consistent interfaces across AWS, GCP, and Azure.

## Active Components

| Component | Type | Description |
|-----------|------|-------------|
| `CloudProvider` | Enum | AWS, GCP, AZURE, LOCAL identifiers |
| `ResourceType` | Enum | COMPUTE, STORAGE, DATABASE, etc. |
| `CloudCredentials` | Dataclass | Provider credentials container |
| `CloudResource` | Dataclass | Generic resource representation |
| `CloudClient` | ABC | Generic resource management interface |
| `StorageClient` | ABC | Object storage interface |
| `ComputeClient` | ABC | VM/Instance management interface |
| `ServerlessClient` | ABC | FaaS interface |
| `CloudConfig` | Class | Multi-provider configuration manager |

## Operating Contracts

### Import Pattern

```python
from codomyrmex.cloud.common import (
    CloudProvider,
    ResourceType,
    CloudCredentials,
    CloudResource,
    StorageClient,
    ComputeClient,
    ServerlessClient,
    CloudConfig,
)
```

### Implementing Custom Clients

When creating provider-specific implementations:

1. Inherit from appropriate ABC (`StorageClient`, `ComputeClient`, etc.)
2. Implement ALL abstract methods
3. Handle provider exceptions internally
4. Use consistent return types as specified in contracts
5. Log errors using Python `logging` module

## Modification Guidelines

- **Adding New ABCs**: Follow existing pattern with `@abstractmethod` decorators
- **Extending Enums**: Add new values to `CloudProvider` or `ResourceType` as needed
- **Updating Dataclasses**: Maintain backward compatibility with optional fields

## Navigation

- **📁 Parent**: [cloud/](../README.md)
- **📖 Specification**: [SPEC.md](SPEC.md)
