# encryption/containers Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Purpose

The `encryption/containers` submodule provides `SecureDataContainer`, a high-level abstraction for encrypting arbitrary Python objects. It serializes data and optional metadata to JSON, then encrypts the payload using AES-GCM authenticated encryption. This is the recommended way to store encrypted structured data.

## 3.1 Interface / API

### Class: `SecureDataContainer`

```python
SecureDataContainer(key: bytes)
```

**Constructor parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `key` | `bytes` | AES key (16, 24, or 32 bytes) passed to the internal `AESGCMEncryptor` |

**Methods:**

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `pack(data, metadata)` | `data: Any`, `metadata: dict[str, Any] \| None = None` | `bytes` | Serialize `{"data": data, "metadata": metadata}` to JSON, encrypt with AES-GCM |
| `unpack(encrypted_data)` | `encrypted_data: bytes` | `dict[str, Any]` | Decrypt and deserialize; returns dict with `"data"` and `"metadata"` keys |

### Wire Format

`pack()` output is the AES-GCM wire format: `nonce (12B) || ciphertext || tag (16B)`.

The JSON payload structure is:
```json
{"data": <any JSON-serializable value>, "metadata": {}}
```

### Exceptions

- `ValueError` from `AESGCMEncryptor` if key size is invalid.
- `cryptography.exceptions.InvalidTag` if ciphertext is tampered during `unpack()`.
- `json.JSONDecodeError` if decrypted payload is not valid JSON.
- `TypeError` if `data` is not JSON-serializable during `pack()`.

## 5 Configuration

No external configuration. The container delegates all cryptography to `encryption.algorithms.AESGCMEncryptor`. The only required input is a valid AES key.
