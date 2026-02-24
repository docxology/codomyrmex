# encryption/containers

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Secure data containers for encrypted object storage. Provides `SecureDataContainer`, which serializes Python objects (and optional metadata) to JSON and encrypts them using AES-GCM authenticated encryption. This is the highest-level encryption interface in the stack -- pass in any JSON-serializable data and get back an opaque encrypted blob that detects tampering on decryption.

## Quick Start

```python
from codomyrmex.encryption.containers import SecureDataContainer
import os

key = os.urandom(32)  # 256-bit AES key
container = SecureDataContainer(key)

# Pack: serialize + encrypt
blob = container.pack(
    data={"user": "alice", "scores": [98, 87, 95]},
    metadata={"version": 1, "created": "2026-02-24"},
)

# Unpack: decrypt + deserialize
result = container.unpack(blob)
print(result["data"])      # {"user": "alice", "scores": [98, 87, 95]}
print(result["metadata"])  # {"version": 1, "created": "2026-02-24"}
```

## API Reference

| Export | Type | Description |
|--------|------|-------------|
| `SecureDataContainer` | class | JSON-serialize + AES-GCM encrypt/decrypt for structured data |

### `SecureDataContainer` Methods

| Method | Signature | Description |
|--------|-----------|-------------|
| `__init__` | `(key: bytes)` | Create container with AES key (16/24/32 bytes) |
| `pack` | `(data: Any, metadata: dict \| None = None) -> bytes` | Serialize and encrypt |
| `unpack` | `(encrypted_data: bytes) -> dict[str, Any]` | Decrypt and deserialize |

## Dependencies

- `encryption.algorithms.AESGCMEncryptor` (internal)
- Standard library `json`
