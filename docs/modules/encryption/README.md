# Encryption Module Documentation

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Cryptographic operations: encryption, hashing, signing, and key management.

## Key Features

- **Symmetric** — AES encryption
- **Asymmetric** — RSA, EC cryptography
- **Hashing** — SHA-256, bcrypt, argon2
- **Keys** — Key generation and storage

## Quick Start

```python
from codomyrmex.encryption import encrypt, decrypt, hash_password

# Encrypt data
encrypted = encrypt(data, key)
decrypted = decrypt(encrypted, key)

# Hash passwords
hashed = hash_password("secret123")
is_valid = verify_password("secret123", hashed)
```

## Directory Contents

| File | Description |
|------|-------------|
| `README.md` | This file |
| `SPEC.md` | Technical specification |

## Navigation

- **Source**: [src/codomyrmex/encryption/](../../../src/codomyrmex/encryption/)
- **Parent**: [Modules](../README.md)
