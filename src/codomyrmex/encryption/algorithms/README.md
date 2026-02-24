# encryption/algorithms

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Authenticated encryption implementations for the codomyrmex encryption stack. Currently provides `AESGCMEncryptor`, which wraps AES-GCM (Galois/Counter Mode) to deliver both confidentiality and integrity in a single encrypt call. This is the recommended symmetric cipher for all new code, replacing the legacy AES-CBC mode in `encryption/core`.

## Quick Start

```python
from codomyrmex.encryption.algorithms import AESGCMEncryptor

# Auto-generate a 256-bit key
enc = AESGCMEncryptor()

# Encrypt with optional authenticated associated data
ciphertext = enc.encrypt(b"secret payload", associated_data=b"header-v1")

# Decrypt (raises InvalidTag if tampered)
plaintext = enc.decrypt(ciphertext, associated_data=b"header-v1")

# Use a specific key
key = enc.key  # retrieve the auto-generated key
enc2 = AESGCMEncryptor(key=key)  # reuse for decryption elsewhere
```

## API Reference

| Export | Type | Description |
|--------|------|-------------|
| `AESGCMEncryptor` | class | AES-GCM authenticated encryption with auto-nonce |

### `AESGCMEncryptor` Methods

| Method | Signature | Description |
|--------|-----------|-------------|
| `__init__` | `(key: bytes \| None = None)` | Create encryptor; auto-generates 32-byte key if none given |
| `encrypt` | `(data: bytes, associated_data: bytes \| None = None) -> bytes` | Encrypt with fresh 12-byte nonce; returns `nonce \|\| ciphertext \|\| tag` |
| `decrypt` | `(data: bytes, associated_data: bytes \| None = None) -> bytes` | Decrypt and verify; raises `InvalidTag` on failure |

## Dependencies

- `cryptography` (AESGCM from hazmat.primitives.ciphers.aead)
