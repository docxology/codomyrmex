# Agent Guidelines - Encryption

## Module Overview

Cryptographic operations: symmetric, asymmetric, hashing, and key management.

## Key Classes

- **SymmetricEncryptor** — AES encryption
- **AsymmetricEncryptor** — RSA/EC encryption
- **KeyManager** — Key generation and storage
- **Hasher** — Secure hashing (SHA-256/512)

## Agent Instructions

1. **Use strong keys** — AES-256, RSA-2048 minimum
2. **Rotate keys** — Regular key rotation
3. **Store securely** — Never log or expose keys
4. **Use authenticated** — Prefer AEAD modes (GCM)
5. **Salt hashes** — Always use salt for passwords

## Common Patterns

```python
from codomyrmex.encryption import (
    SymmetricEncryptor, AsymmetricEncryptor, KeyManager, Hasher
)

# Symmetric encryption
encryptor = SymmetricEncryptor()
key = encryptor.generate_key()
ciphertext = encryptor.encrypt(plaintext, key)
decrypted = encryptor.decrypt(ciphertext, key)

# Asymmetric encryption
asym = AsymmetricEncryptor()
public_key, private_key = asym.generate_keypair()
encrypted = asym.encrypt(data, public_key)
decrypted = asym.decrypt(encrypted, private_key)

# Key management
manager = KeyManager()
manager.store_key("api_key", key, rotate_days=90)

# Secure hashing
hasher = Hasher()
hash_value = hasher.hash_password(password, salt=generate_salt())
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
