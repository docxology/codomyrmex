# encryption/keys Personal AI Infrastructure

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## AI Capabilities

This module exposes the following capabilities for AI agent use:

- **Store encryption keys** -- Persist key bytes to disk with restrictive file permissions via `KeyManager.store_key(key_id, key)`
- **Retrieve encryption keys** -- Load stored keys by identifier via `KeyManager.get_key(key_id)`
- **Delete encryption keys** -- Securely remove key files via `KeyManager.delete_key(key_id)`
- **List all stored keys** -- Enumerate available key identifiers via `KeyManager.list_keys()`
- **Check key existence** -- Verify a key exists without loading it via `KeyManager.key_exists(key_id)`
- **Rotate keys** -- Replace a key and receive the old key for re-encryption via `KeyManager.rotate_key(key_id, new_key)`
- **Derive keys from shared secrets** -- Use HKDF (SHA-256/384/512) to derive encryption keys from high-entropy material via `derive_key_hkdf()`
- **Compute HMAC** -- Generate HMAC digests for message authentication via `compute_hmac(data, key)`
- **Verify HMAC** -- Constant-time HMAC verification to prevent timing attacks via `verify_hmac(data, key, expected_mac)`

## Usage Notes for Agents

- `KeyManager` defaults to a temp directory; pass a custom `key_dir` for persistent storage.
- `derive_key_hkdf` is for high-entropy inputs only (DH shared secrets, etc.). For passwords, use `Encryptor.derive_key()` from `encryption.core`.
- HMAC verification uses constant-time comparison; always prefer `verify_hmac` over manual comparison.
