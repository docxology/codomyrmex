# encryption/core Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Purpose

The `encryption/core` submodule provides the primary `Encryptor` class and convenience functions for symmetric (AES-256-CBC) and asymmetric (RSA-OAEP) encryption, key generation, digital signatures (RSA-PSS), file encryption, and hashing. AES-CBC mode is considered legacy; prefer `encryption/algorithms` (AES-GCM) for new code.

## 3.1 Interface / API

### Class: `Encryptor`

```python
Encryptor(algorithm: str = "AES")
```

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `encrypt(data, key)` | `data: bytes`, `key: bytes` | `bytes` | Encrypt data using configured algorithm (AES-CBC or RSA-OAEP) |
| `decrypt(data, key)` | `data: bytes`, `key: bytes` | `bytes` | Decrypt data using configured algorithm |
| `generate_key()` | none | `bytes` | Generate a random key (32-byte AES or 2048-bit RSA PEM) |
| `derive_key(password, salt)` | `password: str`, `salt: bytes` | `bytes` | Derive AES key from password using PBKDF2-SHA256 (100k iterations) |
| `sign(data, private_key)` | `data: bytes`, `private_key: bytes` | `bytes` | RSA-PSS signature over data |
| `verify(data, signature, public_key)` | `data: bytes`, `signature: bytes`, `public_key: bytes` | `bool` | Verify RSA-PSS signature |
| `encrypt_string(plaintext, key, encoding)` | `plaintext: str`, `key: bytes`, `encoding: str = "utf-8"` | `str` | Encrypt string, return base64 ciphertext |
| `decrypt_string(ciphertext, key, encoding)` | `ciphertext: str`, `key: bytes`, `encoding: str = "utf-8"` | `str` | Decrypt base64 ciphertext to string |
| `encrypt_file(input_path, output_path, key)` | `input_path: str`, `output_path: str`, `key: bytes` | `bool` | Encrypt file on disk |
| `decrypt_file(input_path, output_path, key)` | `input_path: str`, `output_path: str`, `key: bytes` | `bool` | Decrypt file on disk |
| `hash_data(data, algorithm)` | `data: bytes`, `algorithm: str = "sha256"` | `str` | Compute hex hash (sha256/sha512/sha384/md5) |
| `generate_salt(length)` | `length: int = 16` | `bytes` | Generate random salt |
| `generate_key_pair(key_size)` | `key_size: int = 2048` | `tuple[bytes, bytes]` | Generate RSA (private_pem, public_pem) |

### Convenience Functions

| Function | Signature | Description |
|----------|-----------|-------------|
| `encrypt_data` | `(data: bytes, key: bytes, algorithm: str = "AES") -> bytes` | Module-level encrypt shortcut |
| `decrypt_data` | `(data: bytes, key: bytes, algorithm: str = "AES") -> bytes` | Module-level decrypt shortcut |
| `generate_aes_key` | `() -> bytes` | Generate random 32-byte AES-256 key |

### Exceptions

All encryption/decryption failures raise `codomyrmex.exceptions.EncryptionError`.

## 5 Configuration

No external configuration is required. The module depends on the `cryptography` library. Key parameters:

- AES key length: 32 bytes (256-bit). Keys of other lengths are SHA-256 hashed to 32 bytes.
- AES mode: CBC with PKCS7 padding. IV is 16 bytes, prepended to ciphertext.
- RSA key size: 2048-bit default, OAEP padding with SHA-256.
- PBKDF2: SHA-256, 100,000 iterations, 32-byte output.
- Digital signatures: RSA-PSS with SHA-256 and MGF1.

## Deprecation Notice

AES-CBC mode (used by `Encryptor(algorithm="AES")`) does not provide authentication and emits a `DeprecationWarning`. Use `encryption.algorithms.AESGCMEncryptor` for authenticated encryption in new code.
