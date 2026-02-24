# encryption/keys Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Purpose

The `encryption/keys` submodule provides key management, key derivation, and message authentication. It contains three components: `KeyManager` for file-based key storage with restricted permissions, `derive_key_hkdf` for HKDF-based key derivation from high-entropy material, and `compute_hmac`/`verify_hmac` for HMAC computation and constant-time verification.

## 3.1 Interface / API

### Class: `KeyManager`

```python
KeyManager(key_dir: Path | None = None)
```

Default `key_dir`: `$TMPDIR/codomyrmex_keys/`. Directory is created if absent. Key files are stored as `{key_id}.key` with mode `0o600`.

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `store_key(key_id, key)` | `key_id: str`, `key: bytes` | `bool` | Store key bytes to disk with 0600 permissions |
| `get_key(key_id)` | `key_id: str` | `bytes \| None` | Retrieve key by ID, or `None` if absent |
| `delete_key(key_id)` | `key_id: str` | `bool` | Delete key file; `False` if not found |
| `list_keys()` | none | `list[str]` | List all stored key IDs (sorted) |
| `key_exists(key_id)` | `key_id: str` | `bool` | Check if key exists without loading |
| `rotate_key(key_id, new_key)` | `key_id: str`, `new_key: bytes` | `bytes \| None` | Replace key, return old key (for re-encryption) |

### Function: `derive_key_hkdf`

```python
derive_key_hkdf(
    input_key_material: bytes | str,
    length: int = 32,
    salt: bytes | None = None,
    info: bytes | None = None,
    algorithm: str = "sha256",
) -> bytes
```

HKDF derivation from high-entropy input (shared secrets, DH outputs). Not for passwords -- use `Encryptor.derive_key()` (PBKDF2) for that. Supported algorithms: `sha256`, `sha384`, `sha512`.

### Function: `compute_hmac`

```python
compute_hmac(
    data: bytes | str,
    key: bytes | str,
    algorithm: str = "sha256",
) -> bytes
```

Compute raw HMAC digest bytes. Accepts `str` inputs (auto-encoded as UTF-8). Supported algorithms: `sha256`, `sha384`, `sha512`.

### Function: `verify_hmac`

```python
verify_hmac(
    data: bytes | str,
    key: bytes | str,
    expected_mac: bytes,
    algorithm: str = "sha256",
) -> bool
```

Verify HMAC using constant-time comparison (`hmac.compare_digest`).

## 5 Configuration

- **Key storage directory**: Defaults to `$TMPDIR/codomyrmex_keys/`. Override via `KeyManager(key_dir=Path(...))`.
- **File permissions**: Keys stored with `chmod 0o600` (owner-only read/write).
- **HKDF**: Uses `cryptography` library HKDF implementation.
- **HMAC**: Uses stdlib `hmac` module for constant-time comparison.
