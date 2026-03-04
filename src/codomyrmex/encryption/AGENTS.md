# Agent Guidelines - Encryption

**Version**: v1.1.0 | **Status**: Active | **Last Updated**: March 2026

## Module Overview

Cryptographic operations: symmetric encryption (AES-CBC legacy and AES-GCM authenticated), asymmetric encryption (RSA-OAEP), digital signatures (RSA-PSS and HMAC), key derivation (PBKDF2 and HKDF), and secure key management. The `AESGCMEncryptor` is the recommended symmetric cipher for all new work; `Encryptor` retains AES-CBC for backward compatibility but emits a `DeprecationWarning`. `KeyManager` provides file-based key storage with restrictive permissions (0o600). `SecureDataContainer` wraps AES-GCM for encrypting JSON-serializable Python objects. `Signer` offers fast HMAC-based signing and verification for JSON payloads and files.

## Key Files

| File | Purpose |
|------|---------|
| `__init__.py` | Exports `Encryptor`, `AESGCMEncryptor`, `KeyManager`, `SecureDataContainer`, `Signer`, convenience functions (`encrypt`, `decrypt`, `generate_key`, `hash_data`, `encrypt_file`, `decrypt_file`) |
| `core/encryptor.py` | `Encryptor` class: AES-CBC (legacy), RSA-OAEP encryption, RSA-PSS signing, PBKDF2 key derivation, file encryption, hashing |
| `algorithms/aes_gcm.py` | `AESGCMEncryptor`: authenticated symmetric encryption with optional AAD; 12-byte nonce + 16-byte tag |
| `keys/key_manager.py` | `KeyManager`: file-based key storage, retrieval, rotation, listing, deletion with 0o600 permissions |
| `keys/kdf.py` | `derive_key_hkdf()`: HKDF key derivation from high-entropy material (SHA-256/384/512) |
| `keys/hmac_utils.py` | `compute_hmac()` and `verify_hmac()`: HMAC computation and constant-time verification |
| `signing.py` | `Signer`, `SignatureResult`, `SignatureAlgorithm`: HMAC-based JSON and file signing/verification |
| `containers/container.py` | `SecureDataContainer`: encrypted storage for JSON-serializable Python objects via AES-GCM |

## Key Classes

- **AESGCMEncryptor** -- Authenticated symmetric encryption using AES-GCM (recommended). Accepts 16/24/32-byte keys; auto-generates 32-byte key if none provided. `encrypt()` returns nonce+ciphertext+tag; `decrypt()` verifies authenticity.
- **Encryptor** -- Legacy symmetric (AES-CBC) and asymmetric (RSA-OAEP) encryption. Also provides `sign()`, `verify()`, `derive_key()`, `hash_data()`, `generate_key_pair()`, and file encryption utilities.
- **KeyManager** -- File-based key storage with `store_key()`, `get_key()`, `delete_key()`, `list_keys()`, `key_exists()`, `rotate_key()`. Keys stored as `{key_id}.key` with 0o600 permissions.
- **Signer** -- HMAC-based signing (SHA-256 or SHA-512). `sign()` returns `SignatureResult`; `sign_json()` embeds `_signature` field; `verify()` and `verify_json()` use constant-time comparison.
- **SecureDataContainer** -- Encrypts JSON-serializable objects via AES-GCM. `pack()` serializes and encrypts; `unpack()` decrypts and deserializes.

## Agent Instructions

1. **Use AES-GCM, not AES-CBC** -- Always use `AESGCMEncryptor` for symmetric encryption. `Encryptor` AES mode is CBC-only and emits a `DeprecationWarning`.
2. **Always use AAD when context is available** -- Pass `associated_data` to `AESGCMEncryptor.encrypt()` to bind ciphertext to its context (e.g., a record ID or version tag).
3. **Never log or print keys** -- Key bytes must never appear in log messages, error contexts, or debug output. Log the `key_id` instead.
4. **Use KeyManager for persistence** -- Do not write key bytes to arbitrary files. Use `KeyManager.store_key()` which enforces 0o600 permissions.
5. **Rotate keys via KeyManager** -- Call `KeyManager.rotate_key(key_id, new_key)` which atomically returns the old key before storing the replacement.
6. **Prefer HKDF for derived keys** -- Use `derive_key_hkdf()` for deriving keys from shared secrets. Use `Encryptor.derive_key()` (PBKDF2) only for password-based derivation.
7. **Verify round-trip in tests** -- Always assert `decrypt(encrypt(plaintext)) == plaintext` and that tampered ciphertext raises `EncryptionError`.

## Operating Contracts

- AES-GCM is the mandatory cipher for all new symmetric encryption work; AES-CBC is retained only for decrypting legacy data.
- `AESGCMEncryptor` keys must be exactly 16, 24, or 32 bytes; any other length raises `ValueError`.
- `AESGCMEncryptor.decrypt()` requires data of at least 28 bytes (12-byte nonce + 16-byte tag); shorter data raises `EncryptionError`.
- `KeyManager.rotate_key()` stores the new key unconditionally; it returns `None` if no prior key existed (not an error).
- `KeyManager` file permissions are set to 0o600 (owner read/write only) after every `store_key()` call.
- Raw key bytes must not be held in memory longer than needed; dereference key variables after use.
- All cryptographic failures raise `EncryptionError` (from `codomyrmex.exceptions`), never bare `Exception`.
- `Signer.verify()` and `verify_hmac()` use constant-time comparison to prevent timing attacks.
- **DO NOT** use `Encryptor` AES mode for new data -- it provides no authentication and is vulnerable to padding oracle attacks.

## Common Patterns

### Symmetric Authenticated Encryption (Recommended)

```python
from codomyrmex.encryption import AESGCMEncryptor, generate_key

key = generate_key("AES")  # 32 bytes
gcm = AESGCMEncryptor(key)
# Encrypt and decrypt with optional associated data
ciphertext = gcm.encrypt(b"Secret data", associated_data=b"context-v1")
plaintext = gcm.decrypt(ciphertext, associated_data=b"context-v1")
```

### Digital Signatures (HMAC)

```python
from codomyrmex.encryption import Signer

signer = Signer(secret_key="my_secret")
# Sign entire JSON objects
signed_msg = signer.sign_json({"action": "deploy", "id": 789})
if signer.verify_json(signed_msg):
    print("Valid signature")
```

### Key Management

```python
from codomyrmex.encryption import KeyManager
from pathlib import Path

km = KeyManager(key_dir=Path("./agent_keys"))
key = b"..."
km.store_key("main_vault", key)

if km.key_exists("main_vault"):
    key_bytes = km.get_key("main_vault")
```

## Testing Patterns (Zero-Mock Mandatory)

Always use the actual `cryptography` library for testing; do **not** mock encryption or signing results.

```python
# Verify encryption round-trip
key = generate_key("AES")
gcm = AESGCMEncryptor(key)
plaintext = b"secret data"
ciphertext = gcm.encrypt(plaintext)
assert gcm.decrypt(ciphertext) == plaintext

# Verify tampering is detected
tampered = bytearray(ciphertext)
tampered[-1] ^= 0xFF
with pytest.raises(EncryptionError):
    gcm.decrypt(bytes(tampered))
```

## PAI Agent Role Access Matrix

| PAI Agent | Access Level | Primary Capabilities | Trust Level |
|-----------|-------------|---------------------|-------------|
| **Engineer** | Full | Symmetric/asymmetric encryption, key management, data-at-rest/in-transit protection | TRUSTED |
| **Architect** | Read + Design | Encryption strategy review, key lifecycle design, security architecture | OBSERVED |
| **QATester** | Validation | Encryption correctness, key rotation testing, data protection verification | OBSERVED |
| **Researcher** | Read-only | Inspect encryption algorithms and key structures for analysis | SAFE |

### Engineer Agent
**Use Cases**: Encrypting sensitive data during BUILD/EXECUTE, managing encryption keys, signing artifacts.

### Architect Agent
**Use Cases**: Reviewing encryption strategies, designing key management, planning security architecture.

### QATester Agent
**Use Cases**: Verifying encryption correctness during VERIFY, testing key rotation, tamper detection.

### Researcher Agent
**Use Cases**: Inspecting encryption algorithms and key management patterns for security analysis.

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)


## Rule Reference

This module is governed by the following rule file:

- [`src/codomyrmex/agentic_memory/rules/modules/encryption.cursorrules`](src/codomyrmex/agentic_memory/rules/modules/encryption.cursorrules)
