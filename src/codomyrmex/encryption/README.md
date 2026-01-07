# encryption

## Signposting
- **Parent**: [codomyrmex](../README.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [Agent Guide](AGENTS.md)
    - [Functional Spec](SPEC.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Overview

Encryption/decryption utilities and key management. Provides algorithm-agnostic encryption interface with support for AES and RSA algorithms, key derivation from passwords, digital signatures, and secure key storage with restrictive file permissions.

## Directory Contents
- `README.md` – File
- `SPEC.md` – File
- `__init__.py` – File
- `encryptor.py` – File
- `key_manager.py` – File

## Navigation
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: [README](../../../README.md)

## Getting Started

To use this module in your project, import the necessary components:

```python
from codomyrmex.encryption import Encryptor, KeyManager, encrypt, decrypt, generate_key

# Basic encryption/decryption
encryptor = Encryptor(algorithm="AES")
key = encryptor.generate_key()
data = b"Secret data"
encrypted = encryptor.encrypt(data, key)
decrypted = encryptor.decrypt(encrypted, key)

# Key derivation from password
salt = os.urandom(16)
derived_key = encryptor.derive_key("my_password", salt)

# Digital signatures
private_key = encryptor.generate_key()  # For RSA
signature = encryptor.sign(data, private_key)
is_valid = encryptor.verify(data, signature, public_key)

# Key management
key_manager = KeyManager()
key_manager.store_key("my_key_id", key)
retrieved_key = key_manager.get_key("my_key_id")
```

