# Encryption Module API Specification

**Version**: v0.1.7 | **Status**: Stable | **Last Updated**: February 2026

## 1. Overview

The `encryption` module provides secure cryptographic primitives for Codomyrmex. It wraps the `cryptography` library and the standard library to offer simplified interfaces for symmetric/asymmetric encryption, authenticated encryption, HMAC, key derivation, and secure hashing.

## 2. Classes

### 2.1 `Encryptor`

Main encryption class supporting AES-CBC and RSA algorithms.

```python
class Encryptor:
    def __init__(self, algorithm: str = "AES") -> None
```

| Method | Signature | Description |
|--------|-----------|-------------|
| `encrypt` | `(data: bytes, key: bytes) -> bytes` | Encrypt data |
| `decrypt` | `(data: bytes, key: bytes) -> bytes` | Decrypt data |
| `generate_key` | `() -> bytes` | Generate key for the configured algorithm |
| `derive_key` | `(password: str, salt: bytes) -> bytes` | PBKDF2 key derivation |
| `sign` | `(data: bytes, private_key: bytes) -> bytes` | RSA-PSS digital signature |
| `verify` | `(data: bytes, signature: bytes, public_key: bytes) -> bool` | Verify signature |
| `encrypt_string` | `(plaintext: str, key: bytes, encoding: str = "utf-8") -> str` | Encrypt string, return base64 |
| `decrypt_string` | `(ciphertext: str, key: bytes, encoding: str = "utf-8") -> str` | Decrypt base64 to string |
| `encrypt_file` | `(input_path: str, output_path: str, key: bytes) -> bool` | Encrypt a file |
| `decrypt_file` | `(input_path: str, output_path: str, key: bytes) -> bool` | Decrypt a file |
| `hash_data` | `(data: bytes, algorithm: str = "sha256") -> str` | Compute hex digest (static) |
| `generate_salt` | `(length: int = 16) -> bytes` | Generate random salt (static) |
| `generate_key_pair` | `(key_size: int = 2048) -> Tuple[bytes, bytes]` | Generate RSA key pair |

### 2.2 `AESGCMEncryptor`

Authenticated encryption using AES-GCM. Recommended over AES-CBC.

```python
class AESGCMEncryptor:
    def __init__(self, key: Optional[bytes] = None) -> None
```

| Method | Signature | Description |
|--------|-----------|-------------|
| `encrypt` | `(data: bytes, associated_data: Optional[bytes] = None) -> bytes` | Encrypt with optional AAD |
| `decrypt` | `(data: bytes, associated_data: Optional[bytes] = None) -> bytes` | Decrypt and verify |

### 2.3 `SecureDataContainer`

Encrypts JSON-serializable Python objects using AES-GCM.

```python
class SecureDataContainer:
    def __init__(self, key: bytes) -> None
```

| Method | Signature | Description |
|--------|-----------|-------------|
| `pack` | `(data: Any, metadata: Optional[Dict] = None) -> bytes` | Serialize and encrypt |
| `unpack` | `(encrypted_data: bytes) -> Dict[str, Any]` | Decrypt and deserialize |

### 2.4 `KeyManager`

File-based key storage with restrictive permissions.

```python
class KeyManager:
    def __init__(self, key_dir: Optional[Path] = None) -> None
```

| Method | Signature | Description |
|--------|-----------|-------------|
| `store_key` | `(key_id: str, key: bytes) -> bool` | Store key with 0o600 perms |
| `get_key` | `(key_id: str) -> Optional[bytes]` | Retrieve stored key |
| `delete_key` | `(key_id: str) -> bool` | Delete stored key |
| `list_keys` | `() -> list[str]` | List all stored key IDs |
| `key_exists` | `(key_id: str) -> bool` | Check if key exists |
| `rotate_key` | `(key_id: str, new_key: bytes) -> Optional[bytes]` | Replace key, return old |

## 3. Standalone Functions

### 3.1 Convenience (from `__init__.py`)

| Function | Signature | Description |
|----------|-----------|-------------|
| `encrypt` | `(data: bytes, key: bytes, algorithm: str = "AES") -> bytes` | One-shot encrypt |
| `decrypt` | `(data: bytes, key: bytes, algorithm: str = "AES") -> bytes` | One-shot decrypt |
| `generate_key` | `(algorithm: str = "AES") -> bytes` | Generate key |
| `get_encryptor` | `(algorithm: str = "AES") -> Encryptor` | Factory |
| `encrypt_file` | `(input_path, output_path, key, algorithm="AES") -> bool` | File encrypt |
| `decrypt_file` | `(input_path, output_path, key, algorithm="AES") -> bool` | File decrypt |
| `hash_data` | `(data: bytes, algorithm: str = "sha256") -> str` | Hash data |
| `encrypt_data` | `(data: bytes, key: bytes, algorithm: str = "AES") -> bytes` | Legacy encrypt helper |
| `decrypt_data` | `(data: bytes, key: bytes, algorithm: str = "AES") -> bytes` | Legacy decrypt helper |
| `generate_aes_key` | `() -> bytes` | Generate 32-byte AES key |

### 3.2 HMAC (from `hmac_utils.py`)

| Function | Signature | Description |
|----------|-----------|-------------|
| `compute_hmac` | `(data, key, algorithm="sha256") -> bytes` | Compute HMAC digest |
| `verify_hmac` | `(data, key, expected_mac, algorithm="sha256") -> bool` | Constant-time verify |

### 3.3 Key Derivation (from `kdf.py`)

| Function | Signature | Description |
|----------|-----------|-------------|
| `derive_key_hkdf` | `(input_key_material, length=32, salt=None, info=None, algorithm="sha256") -> bytes` | HKDF derivation |

## 4. Exceptions

| Exception | Base | Description |
|-----------|------|-------------|
| `EncryptionError` | `CodomyrmexError` | All cryptographic operation failures |

Defined in `codomyrmex.exceptions` and re-exported by this module.

## 5. Usage Examples

### AES-GCM (Recommended)

```python
from codomyrmex.encryption import AESGCMEncryptor, generate_aes_key

key = generate_aes_key()
gcm = AESGCMEncryptor(key)
ct = gcm.encrypt(b"Secret", associated_data=b"header")
pt = gcm.decrypt(ct, associated_data=b"header")
```

### HMAC Verification

```python
from codomyrmex.encryption import compute_hmac, verify_hmac

mac = compute_hmac(b"payload", b"secret")
assert verify_hmac(b"payload", b"secret", mac)
```

### HKDF Key Derivation

```python
from codomyrmex.encryption import derive_key_hkdf

key = derive_key_hkdf(b"dh-shared-secret", length=32, info=b"session-key-v1")
```

### Key Rotation

```python
from codomyrmex.encryption import KeyManager, AESGCMEncryptor
import os

km = KeyManager()
km.store_key("app-key", os.urandom(32))

new_key = os.urandom(32)
old_key = km.rotate_key("app-key", new_key)

# Re-encrypt data from old_key to new_key
old_enc = AESGCMEncryptor(old_key)
new_enc = AESGCMEncryptor(new_key)
plaintext = old_enc.decrypt(ciphertext)
new_ciphertext = new_enc.encrypt(plaintext)
```
