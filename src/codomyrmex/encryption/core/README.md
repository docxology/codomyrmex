# encryption/core

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Core encryption engine providing the `Encryptor` class for AES-256-CBC symmetric encryption, RSA-OAEP asymmetric encryption, PBKDF2 key derivation, RSA-PSS digital signatures, file encryption, and hashing. Module-level convenience functions `encrypt_data`, `decrypt_data`, and `generate_aes_key` are re-exported for quick access. Note that AES-CBC mode is legacy; use `encryption.algorithms.AESGCMEncryptor` for authenticated encryption in new code.

## Quick Start

```python
from codomyrmex.encryption.core import encrypt_data, decrypt_data, generate_aes_key, Encryptor

# Symmetric encryption (AES-256-CBC)
key = generate_aes_key()  # 32-byte random key
ciphertext = encrypt_data(b"secret message", key)
plaintext = decrypt_data(ciphertext, key)

# String encryption
enc = Encryptor("AES")
b64_cipher = enc.encrypt_string("hello world", key)
original = enc.decrypt_string(b64_cipher, key)

# RSA key pair and digital signature
enc_rsa = Encryptor("RSA")
private_pem, public_pem = enc_rsa.generate_key_pair(2048)
signature = enc_rsa.sign(b"data to sign", private_pem)
valid = enc_rsa.verify(b"data to sign", signature, public_pem)

# Password-based key derivation
salt = Encryptor.generate_salt()
derived_key = enc.derive_key("my password", salt)
```

## API Reference

| Export | Type | Description |
|--------|------|-------------|
| `Encryptor` | class | Main encryption class supporting AES and RSA |
| `encrypt_data` | function | `(data, key, algorithm="AES") -> bytes` -- encrypt bytes |
| `decrypt_data` | function | `(data, key, algorithm="AES") -> bytes` -- decrypt bytes |
| `generate_aes_key` | function | `() -> bytes` -- generate 32-byte AES-256 key |

## Dependencies

- `cryptography` (hazmat primitives)
- `codomyrmex.exceptions.EncryptionError`
