# Encryption Module

**Version**: v0.2.0 | **Status**: Active | **Last Updated**: January 2025

## Overview

Encryption and cryptographic operations module for Codomyrmex. Provides symmetric and asymmetric encryption, authenticated encryption, key management, HMAC message authentication, key derivation functions, digital signatures, and secure hashing.

## PAI Integration

| Algorithm Phase | Role | Tools Used |
|----------------|------|-----------|
| **BUILD** | Encrypt sensitive artifacts and generate keys | Direct Python import |
| **EXECUTE** | Encrypt and decrypt data during pipeline operations | Direct Python import |
| **VERIFY** | Validate encryption correctness and HMAC integrity | Direct Python import |

PAI agents access this module via direct Python import through the MCP bridge. The Engineer agent uses `AESGCMEncryptor` and `KeyManager` to protect sensitive data artifacts during BUILD and EXECUTE phases.

## Features

- **AES-256 CBC** symmetric encryption (legacy, emits deprecation warning)
- **AES-GCM** authenticated encryption (recommended for most new code)
- **RSA** asymmetric encryption with OAEP padding
- **Digital signatures** using RSA-PSS and HMAC
- **PBKDF2** password-based key derivation
- **HKDF** key derivation from high-entropy material
- **HMAC** message authentication with constant-time verification
- **Secure hashing** (SHA-256, SHA-384, SHA-512, MD5)
- **Key management** with file-based storage, listing, and rotation
- **SecureDataContainer** for encrypting arbitrary JSON-serializable data

## Installation

```bash
uv add codomyrmex
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
- **`Signer`** — HMAC-based message and JSON signer
- **`EncryptionError`** — Raised when encryption or decryption operations fail

### Convenience Functions
- **`encrypt`** / **`decrypt`** — Encrypt or decrypt data with a given key and algorithm
- **`generate_key`** — Generate an encryption key for the specified algorithm
- **`get_encryptor`** — Get an `Encryptor` instance for a given algorithm
- **`encrypt_data`** / **`decrypt_data`** — Lower-level AES-CBC encryption/decryption functions
- **`generate_aes_key`** — Generate a raw 32-byte AES key
- **`encrypt_file`** / **`decrypt_file`** — Encrypt or decrypt a file from input to output
- **`hash_data`** — Compute a hex hash of data (SHA-256, SHA-384, SHA-512, MD5)
- **`compute_hmac`** / **`verify_hmac`** — HMAC computation and constant-time verification
- **`derive_key_hkdf`** — HKDF key derivation from high-entropy material

## Quick Start

```python
from codomyrmex.encryption import (
    generate_key, encrypt, decrypt,
    AESGCMEncryptor,
    compute_hmac, verify_hmac,
    derive_key_hkdf,
    Signer
)

# --- AES-GCM (Recommended) ---
key = generate_key("AES")  # 32 bytes
gcm = AESGCMEncryptor(key)
ciphertext = gcm.encrypt(b"secret data")
plaintext = gcm.decrypt(ciphertext)

# --- HMAC Signer ---
signer = Signer("my-secret-key")
result = signer.sign("hello world")
assert signer.verify("hello world", result.signature)

# --- HKDF ---
derived = derive_key_hkdf(b"shared-secret", length=32, info=b"app-v1")
```

## Security Notes

- **Prefer AES-GCM** over AES-CBC. CBC mode does not authenticate ciphertext and is vulnerable to padding oracle attacks.
- Key files are stored with `0o600` permissions (owner read/write only) via `KeyManager`.
- HMAC verification uses constant-time comparison to prevent timing attacks.
- RSA encryption uses OAEP padding and signing uses PSS padding (industry standards).

## File Structure

| File | Description |
|------|-------------|
| `core/encryptor.py` | Core `Encryptor` class: AES-CBC, RSA, RSA-PSS signatures, hashing, file encryption |
| `algorithms/aes_gcm.py` | `AESGCMEncryptor` for authenticated encryption |
| `containers/container.py` | `SecureDataContainer` for encrypted JSON storage |
| `keys/key_manager.py` | `KeyManager` for key storage, retrieval, and rotation |
| `keys/hmac_utils.py` | Lower-level HMAC computation and verification |
| `keys/kdf.py` | HKDF key derivation utilities |
| `signing.py` | `Signer` class for HMAC-based signing |
| `__init__.py` | Public API and module-level convenience functions |

## Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k encryption -v
```

## Navigation

- **Functional Spec**: [SPEC.md](SPEC.md)
- **Agent Guidelines**: [AGENTS.md](AGENTS.md)
- **API Specification**: [API_SPECIFICATION.md](API_SPECIFICATION.md)
- **MCP Tools**: [MCP_TOOL_SPECIFICATION.md](MCP_TOOL_SPECIFICATION.md)
- **Security Guide**: [SECURITY.md](SECURITY.md)
- **Full Documentation**: [docs/modules/encryption/](../../../docs/modules/encryption/)
