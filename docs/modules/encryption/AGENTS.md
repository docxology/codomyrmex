# Agent Guidelines - Encryption

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Module Overview

Cryptographic operations: symmetric, asymmetric, hashing, and key management.

## Key Components

| Component | Description |
|-----------|-------------|
| `Encryptor` | Core symmetric (AES) and asymmetric (RSA) encryption |
| `KeyManager` | Secure file-based key storage and rotation |
| `SignatureAlgorithm` | Enumeration of supported HMAC algorithms |
| `Signer` | Fast HMAC-based JSON and file signing |
| `SecureDataContainer` | Encrypted storage for JSON-serializable data |

## Usage for Agents

### Symmetric Encryption

```python
from codomyrmex.encryption import Encryptor

e = Encryptor(algorithm="AES")
key = e.generate_key()
# Encrypt strings directly
ciphertext = e.encrypt_string("Secret data", key)
plaintext = e.decrypt_string(ciphertext, key)
```

### Digital Signatures

```python
from codomyrmex.encryption import Signer

signer = Signer(secret_key="my_secret")
# Sign entire JSON objects
signed_msg = signer.sign_json({"action": "deploy", "id": 789})
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

## Testing Patterns

```python
# Verify encryption round-trip
encryptor = SymmetricEncryptor()
key = encryptor.generate_key()
plaintext = b"secret data"
ciphertext = encryptor.encrypt(plaintext, key)
assert encryptor.decrypt(ciphertext, key) == plaintext

# Verify different keys produce different ciphertext
key2 = encryptor.generate_key()
assert encryptor.encrypt(plaintext, key2) != ciphertext
```

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)
