# encryption/containers -- Agent Context

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Module Summary

The `encryption/containers` submodule provides `SecureDataContainer`, a high-level interface for encrypting and decrypting JSON-serializable Python objects with AES-GCM authenticated encryption.

## When to Use This Module

- You need to encrypt structured data (dicts, lists, mixed types) rather than raw bytes
- You want to attach metadata to encrypted payloads (version info, timestamps, tags)
- You want the simplest possible encrypt/decrypt API with tamper detection built in
- You are storing encrypted objects in a database, file system, or message queue

## Exports

| Name | Kind | Purpose |
|------|------|---------|
| `SecureDataContainer` | class | Pack (serialize+encrypt) and unpack (decrypt+deserialize) Python objects |

## Example Agent Usage

```python
from codomyrmex.encryption.containers import SecureDataContainer
import os

key = os.urandom(32)
sc = SecureDataContainer(key)

# Encrypt a config dict
blob = sc.pack({"api_key": "sk-xxx", "endpoint": "https://api.example.com"})

# Later, decrypt it
config = sc.unpack(blob)
print(config["data"]["api_key"])  # "sk-xxx"
```

## Constraints

- Data passed to `pack()` must be JSON-serializable.
- Key must be 16, 24, or 32 bytes.
- Tampered blobs raise `cryptography.exceptions.InvalidTag` on `unpack()`.
- `unpack()` always returns `{"data": ..., "metadata": {...}}`.

## Relationship to Other Modules

| Module | Relationship |
|--------|-------------|
| `encryption.algorithms` | `SecureDataContainer` uses `AESGCMEncryptor` internally |
| `encryption.keys` | Use `KeyManager` to store/retrieve the container's key |
| `encryption.core` | Lower-level alternative for raw byte encryption |
