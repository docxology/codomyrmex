# encryption/keys

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Key management, derivation, and authentication utilities for the codomyrmex encryption stack. Provides `KeyManager` for file-based key storage with restricted permissions and key rotation, `derive_key_hkdf` for HKDF-based key derivation from high-entropy material, and `compute_hmac`/`verify_hmac` for HMAC computation with constant-time verification.

## Quick Start

```python
from codomyrmex.encryption.keys import (
    KeyManager, derive_key_hkdf, compute_hmac, verify_hmac,
)

# Key storage
km = KeyManager()                         # uses temp dir by default
km.store_key("my-aes-key", key_bytes)     # store with 0600 permissions
retrieved = km.get_key("my-aes-key")      # retrieve by ID
old_key = km.rotate_key("my-aes-key", new_key_bytes)  # rotate, get old key back
print(km.list_keys())                     # ['my-aes-key']

# HKDF key derivation (from shared secret, NOT passwords)
derived = derive_key_hkdf(
    input_key_material=shared_secret,
    length=32,
    salt=salt_bytes,
    info=b"encryption-context",
)

# HMAC
mac = compute_hmac(b"message", b"secret-key", algorithm="sha256")
assert verify_hmac(b"message", b"secret-key", mac)
```

## API Reference

| Export | Type | Description |
|--------|------|-------------|
| `KeyManager` | class | File-based key storage with 0600 permissions, rotation, listing |
| `derive_key_hkdf` | function | HKDF key derivation (sha256/sha384/sha512) from high-entropy input |
| `compute_hmac` | function | Compute raw HMAC digest bytes |
| `verify_hmac` | function | Constant-time HMAC verification |

## Dependencies

- `cryptography` (HKDF)
- Standard library `hmac`, `hashlib`
