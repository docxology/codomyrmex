# encryption

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Encryption and cryptographic operations module for Codomyrmex. Provides symmetric and asymmetric encryption, authenticated encryption, key management, HMAC message authentication, key derivation functions, digital signatures, and secure hashing.

## Features

- **AES-256 CBC** symmetric encryption (legacy, emits deprecation warning)
- **AES-GCM** authenticated encryption (recommended for new code)
- **RSA** asymmetric encryption with OAEP padding
- **Digital signatures** using RSA-PSS
- **PBKDF2** password-based key derivation
- **HKDF** key derivation from high-entropy material
- **HMAC** message authentication with constant-time verification
- **Secure hashing** (SHA-256, SHA-384, SHA-512, MD5)
- **Key management** with file-based storage, listing, rotation
- **SecureDataContainer** for encrypting arbitrary JSON-serializable data


## Installation

```bash
uv pip install codomyrmex
```

Or for development:

```bash
uv sync
```

## Key Exports

### Classes
- **`Encryptor`** — Core encryption class supporting AES-CBC and RSA with signing and hashing
- **`AESGCMEncryptor`** — Authenticated encryption using AES-GCM (recommended over AES-CBC)
- **`KeyManager`** — Key storage, retrieval, listing, and rotation with secure file permissions
- **`SecureDataContainer`** — Encrypted container for arbitrary JSON-serializable data
- **`EncryptionError`** — Raised when encryption or decryption operations fail

### Convenience Functions
- **`encrypt`** / **`decrypt`** — Encrypt or decrypt data with a given key and algorithm
- **`generate_key`** — Generate an encryption key for the specified algorithm
- **`get_encryptor`** — Get an Encryptor instance for a given algorithm
- **`encrypt_data`** / **`decrypt_data`** — Lower-level AES encryption/decryption functions
- **`generate_aes_key`** — Generate a raw AES key
- **`encrypt_file`** / **`decrypt_file`** — Encrypt or decrypt a file in place
- **`hash_data`** — Compute a hash of data (SHA-256, SHA-384, SHA-512, MD5)
- **`compute_hmac`** / **`verify_hmac`** — HMAC computation and constant-time verification
- **`derive_key_hkdf`** — HKDF key derivation from high-entropy material

## Quick Start

```python
from codomyrmex.encryption import (
    generate_key, encrypt, decrypt,
    AESGCMEncryptor,
    compute_hmac, verify_hmac,
    derive_key_hkdf,
)

# --- AES-GCM (recommended) ---
key = generate_key()
gcm = AESGCMEncryptor(key)
ciphertext = gcm.encrypt(b"secret data")
plaintext = gcm.decrypt(ciphertext)

# --- HMAC ---
mac = compute_hmac(b"message", b"secret-key")
assert verify_hmac(b"message", b"secret-key", mac)

# --- HKDF ---
derived = derive_key_hkdf(b"shared-secret", length=32, info=b"app-v1")
```

## Security Notes

- **Prefer AES-GCM** over AES-CBC. CBC mode does not authenticate ciphertext and is vulnerable to padding oracle attacks. The module now emits a `DeprecationWarning` when AES-CBC is used.
- Key files are stored with `0o600` permissions via `KeyManager`.
- HMAC verification uses `hmac.compare_digest()` for timing-safe comparison.

## File Descriptions

| File | Description |
|------|-------------|
| `encryptor.py` | Core `Encryptor` class: AES-CBC, RSA, signing, hashing, file encryption |
| `aes_gcm.py` | `AESGCMEncryptor` for authenticated encryption |
| `container.py` | `SecureDataContainer` for encrypted JSON storage |
| `key_manager.py` | `KeyManager` for key storage, retrieval, listing, rotation |
| `hmac_utils.py` | HMAC computation and constant-time verification |
| `kdf.py` | HKDF key derivation |
| `__init__.py` | Public API and convenience functions |


## Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k encryption -v
```

## Navigation

- **API Specification**: [API_SPECIFICATION.md](API_SPECIFICATION.md)
- **Functional Spec**: [SPEC.md](SPEC.md)
- **MCP Tools**: [MCP_TOOL_SPECIFICATION.md](MCP_TOOL_SPECIFICATION.md)
- **Full Documentation**: [docs/modules/encryption/](../../../docs/modules/encryption/)
- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: ../../../README.md
