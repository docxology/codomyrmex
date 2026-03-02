# Agent Guidelines - Encryption

**Version**: v1.0.6 | **Status**: Active | **Last Updated**: January 2025

## Module Overview

Cryptographic operations: symmetric, asymmetric, hashing, and key management.

## Key Components

| Component | Description |
|-----------|-------------|
| `AESGCMEncryptor` | Recommended symmetric (authenticated) encryption |
| `Encryptor` | Symmetric (AES-CBC) and asymmetric (RSA) encryption |
| `KeyManager` | Secure file-based key storage and rotation |
| `Signer` | Fast HMAC-based JSON and file signing |
| `SecureDataContainer` | Encrypted storage for JSON-serializable data |

## Usage for Agents

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

### Engineer Agent
**Use Cases**: Encrypting sensitive data during BUILD/EXECUTE, managing encryption keys, signing artifacts.

### Architect Agent
**Use Cases**: Reviewing encryption strategies, designing key management, planning security architecture.

### QATester Agent
**Use Cases**: Verifying encryption correctness during VERIFY, testing key rotation.

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)
