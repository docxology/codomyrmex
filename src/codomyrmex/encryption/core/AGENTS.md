# encryption/core -- Agent Context

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Module Summary

The `encryption/core` submodule provides the `Encryptor` class and convenience functions for symmetric and asymmetric encryption, key generation, digital signatures, file encryption, and hashing. This is the legacy encryption engine; for authenticated encryption, prefer `encryption/algorithms`.

## When to Use This Module

- You need to encrypt/decrypt data or files with AES-256 or RSA-OAEP
- You need to generate RSA key pairs or derive keys from passwords (PBKDF2)
- You need to sign data with RSA-PSS and verify signatures
- You need quick hashing (SHA-256, SHA-512, etc.)
- You need a simple one-call interface (`encrypt_data`, `decrypt_data`)

## Exports

| Name | Kind | Purpose |
|------|------|---------|
| `Encryptor` | class | Full-featured encryption class (AES, RSA, sign, verify, file ops, hash) |
| `encrypt_data` | function | Convenience: encrypt bytes with one call |
| `decrypt_data` | function | Convenience: decrypt bytes with one call |
| `generate_aes_key` | function | Generate a random 32-byte AES-256 key |

## Example Agent Usage

```python
from codomyrmex.encryption.core import generate_aes_key, encrypt_data, decrypt_data

key = generate_aes_key()
ct = encrypt_data(b"agent-sensitive payload", key)
pt = decrypt_data(ct, key)
assert pt == b"agent-sensitive payload"
```

## Constraints

- AES-CBC mode emits a `DeprecationWarning`; prefer `AESGCMEncryptor` from `encryption.algorithms`.
- RSA encryption is limited to small payloads due to OAEP overhead.
- All failures raise `EncryptionError`.

## Relationship to Other Modules

| Module | Relationship |
|--------|-------------|
| `encryption.algorithms` | Preferred alternative for authenticated symmetric encryption (AES-GCM) |
| `encryption.keys` | Key management, HKDF derivation, HMAC utilities |
| `encryption.containers` | High-level encrypted object storage built on `algorithms` |
| `crypto.graphy` | Lower-level cryptographic primitives (separate module tree) |
