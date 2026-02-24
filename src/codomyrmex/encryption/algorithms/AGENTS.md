# encryption/algorithms -- Agent Context

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Module Summary

The `encryption/algorithms` submodule provides `AESGCMEncryptor` for authenticated symmetric encryption using AES-GCM. This is the recommended cipher for all new encryption work, replacing the legacy AES-CBC mode in `encryption/core`.

## When to Use This Module

- You need to encrypt data with both confidentiality and integrity guarantees
- You want authenticated encryption (detects tampering automatically)
- You need to attach authenticated-but-unencrypted metadata (AAD) alongside ciphertext
- You are building new encryption workflows (do not use `encryption/core` AES-CBC for new code)

## Exports

| Name | Kind | Purpose |
|------|------|---------|
| `AESGCMEncryptor` | class | AES-GCM authenticated encryption with auto-nonce and AAD support |

## Example Agent Usage

```python
from codomyrmex.encryption.algorithms import AESGCMEncryptor

enc = AESGCMEncryptor()  # auto-generates 256-bit key
ct = enc.encrypt(b"sensitive data", associated_data=b"context-id")
pt = enc.decrypt(ct, associated_data=b"context-id")
assert pt == b"sensitive data"

# Persist the key
key_bytes = enc.key
```

## Constraints

- Key must be 16, 24, or 32 bytes (128/192/256-bit AES). `ValueError` raised otherwise.
- Tampered ciphertext raises `cryptography.exceptions.InvalidTag` on decrypt.
- Each `encrypt()` call uses a unique random nonce; safe for many messages under one key.

## Relationship to Other Modules

| Module | Relationship |
|--------|-------------|
| `encryption.core` | Legacy alternative (AES-CBC, no authentication); use this module instead |
| `encryption.keys` | Use `KeyManager` to store/retrieve keys, `derive_key_hkdf` for derivation |
| `encryption.containers` | `SecureDataContainer` uses `AESGCMEncryptor` internally |
