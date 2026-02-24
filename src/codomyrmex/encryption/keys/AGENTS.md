# encryption/keys -- Agent Context

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Module Summary

The `encryption/keys` submodule provides key lifecycle management (`KeyManager`), HKDF key derivation (`derive_key_hkdf`), and HMAC computation/verification (`compute_hmac`, `verify_hmac`).

## When to Use This Module

- You need to store, retrieve, list, rotate, or delete encryption keys on disk
- You need to derive encryption keys from a shared secret or DH output (use HKDF)
- You need to compute or verify HMACs for message authentication
- You need constant-time comparison to avoid timing attacks on MAC verification

Do **not** use `derive_key_hkdf` for passwords -- use `Encryptor.derive_key()` from `encryption.core` instead.

## Exports

| Name | Kind | Purpose |
|------|------|---------|
| `KeyManager` | class | Store/retrieve/delete/rotate keys with restrictive file permissions |
| `derive_key_hkdf` | function | HKDF key derivation (sha256/sha384/sha512) |
| `compute_hmac` | function | Compute HMAC digest bytes |
| `verify_hmac` | function | Constant-time HMAC verification |

## Example Agent Usage

```python
from codomyrmex.encryption.keys import KeyManager, compute_hmac, verify_hmac
import os

km = KeyManager()
key = os.urandom(32)
km.store_key("session-key", key)

mac = compute_hmac(b"payload", key)
assert verify_hmac(b"payload", key, mac)

old = km.rotate_key("session-key", os.urandom(32))
# old contains the previous key for re-encryption
```

## Constraints

- Default key directory is a temp directory; for persistence, pass a stable `key_dir` path.
- Key files have `0600` permissions; process must own the directory.
- `derive_key_hkdf` requires high-entropy input; it is not password-safe.

## Relationship to Other Modules

| Module | Relationship |
|--------|-------------|
| `encryption.core` | `Encryptor.derive_key()` provides PBKDF2 for passwords |
| `encryption.algorithms` | `AESGCMEncryptor` consumes keys managed by `KeyManager` |
| `encryption.containers` | `SecureDataContainer` can use keys from `KeyManager` |
| `crypto.graphy.kdf` | Additional KDF implementations (argon2id, scrypt, pbkdf2, hkdf) |
