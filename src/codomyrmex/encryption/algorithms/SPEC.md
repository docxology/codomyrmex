# encryption/algorithms Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Purpose

The `encryption/algorithms` submodule provides authenticated encryption via AES-GCM, the recommended symmetric cipher for all new code in the codomyrmex encryption stack. Unlike AES-CBC in `encryption/core`, AES-GCM provides both confidentiality and integrity in a single operation.

## 3.1 Interface / API

### Class: `AESGCMEncryptor`

```python
AESGCMEncryptor(key: bytes | None = None)
```

**Constructor parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `key` | `bytes \| None` | `None` | AES key (16, 24, or 32 bytes). If `None`, a random 32-byte key is generated. |

**Raises:** `ValueError` if key is provided but not 16, 24, or 32 bytes.

**Attributes:**

| Attribute | Type | Description |
|-----------|------|-------------|
| `key` | `bytes` | The AES key in use (read for storage/transfer) |
| `aesgcm` | `AESGCM` | Internal `cryptography` AESGCM instance |

**Methods:**

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `encrypt(data, associated_data)` | `data: bytes`, `associated_data: bytes \| None = None` | `bytes` | Encrypt data with a random 12-byte nonce. AAD is authenticated but not encrypted. Returns `nonce (12B) \|\| ciphertext+tag`. |
| `decrypt(data, associated_data)` | `data: bytes`, `associated_data: bytes \| None = None` | `bytes` | Decrypt data. Expects `nonce (12B) \|\| ciphertext+tag` format. Verifies authenticity. |

**Raises:** `cryptography.exceptions.InvalidTag` on tampered ciphertext during decrypt.

## 5 Configuration

No external configuration. Depends on the `cryptography` library.

- Nonce: 12 bytes, randomly generated per `encrypt()` call
- Tag: 16 bytes (appended to ciphertext by `AESGCM`)
- Supported key sizes: 128-bit (16B), 192-bit (24B), 256-bit (32B); default is 256-bit
- Wire format: `nonce (12 bytes) || ciphertext || tag (16 bytes)`
