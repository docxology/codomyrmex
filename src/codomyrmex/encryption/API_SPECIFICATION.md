# Encryption Module API Specification

**Version**: v0.1.0 | **Status**: Stable | **Last Updated**: January 2026

## 1. Overview
The `encryption` module provides secure cryptographic primitives for Codomyrmex. It wraps standard libraries to offer simplified interfaces for AES symmetric encryption, RSA asymmetric keys, and secure hashing.

## 2. Core Components

### 2.1 Classes
- **`Encryptor`**: The main class for handling encryption sessions.
- **`KeyManager`**: Utility for generating, storing, and rotating keys.

### 2.2 Functions
- `encrypt(data: bytes, key: bytes, algorithm: str = "AES") -> bytes`: One-shot encryption helper.
- `decrypt(data: bytes, key: bytes, algorithm: str = "AES") -> bytes`: One-shot decryption helper.
- `generate_key(algorithm: str = "AES") -> bytes`: Secure key generation.
- `get_encryptor(algorithm: str = "AES") -> Encryptor`: Factory for obtaining encryptor instances.
- `encrypt_file(path: str, key: bytes) -> None`: Encrypts a file in place or to a target.
- `decrypt_file(path: str, key: bytes) -> None`: Decrypts a file.
- `hash_data(data: bytes) -> str`: Generates SHA-256 hash provided as hex string.

## 3. Exceptions
- `EncryptionError`: Base exception for all cryptographic failures (inherited from `CodomyrmexError`).

## 4. Usage Example

```python
from codomyrmex.encryption import generate_key, encrypt, decrypt

# Generate a new AES-256 key
key = generate_key()

# Encrypt sensitive data
data = b"Secret Message"
encrypted = encrypt(data, key)

# Decrypt
original = decrypt(encrypted, key)
assert data == original
```
