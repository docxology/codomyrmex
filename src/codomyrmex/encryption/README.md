# Encryption Module

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Overview

The Encryption module provides comprehensive encryption, decryption, and key management utilities for Codomyrmex, supporting both symmetric and asymmetric encryption algorithms.

## Key Features

- **AES-256 Symmetric Encryption**: Fast, secure data encryption
- **RSA Asymmetric Encryption**: Public/private key encryption
- **Key Management**: Key generation, storage, and derivation
- **Digital Signatures**: Sign and verify data integrity
- **File Encryption**: Encrypt and decrypt files directly
- **Secure Hashing**: Hash data with various algorithms

## Quick Start

```python
from codomyrmex.encryption import (
    encrypt, decrypt, generate_key,
    Encryptor, KeyManager,
    encrypt_data, decrypt_data,
)

# Simple encryption/decryption
key = generate_key(algorithm="AES")
ciphertext = encrypt(b"secret data", key)
plaintext = decrypt(ciphertext, key)

# Using the Encryptor class
encryptor = Encryptor(algorithm="AES")
key = encryptor.generate_key()
encrypted = encryptor.encrypt(b"my secret", key)
decrypted = encryptor.decrypt(encrypted, key)

# Key management
key_manager = KeyManager()
key_manager.store_key("api-key", key)
retrieved_key = key_manager.get_key("api-key")

# Convenience functions
encrypted = encrypt_data(b"data", key)
decrypted = decrypt_data(encrypted, key)
```

## Core Classes

| Class | Description |
|-------|-------------|
| `Encryptor` | Core encryption operations with algorithm selection |
| `KeyManager` | Secure key storage and retrieval |

## Algorithms

| Algorithm | Type | Use Case |
|-----------|------|----------|
| AES-256 | Symmetric | General-purpose data encryption |
| RSA | Asymmetric | Key exchange, digital signatures |

## Convenience Functions

| Function | Description |
|----------|-------------|
| `encrypt(data, key, algorithm)` | Encrypt bytes data |
| `decrypt(data, key, algorithm)` | Decrypt bytes data |
| `generate_key(algorithm)` | Generate an encryption key |
| `get_encryptor(algorithm)` | Get an Encryptor instance |
| `encrypt_data(data, key)` | Quick encrypt helper |
| `decrypt_data(data, key)` | Quick decrypt helper |
| `generate_aes_key()` | Generate AES-256 key |

## Exceptions

| Exception | Description |
|-----------|-------------|
| `EncryptionError` | Encryption/decryption operations failed |

## Navigation

- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: [README](../../../README.md)
