# Crypto Graphy -- Functional Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Core cryptography primitives organized into seven domains: symmetric encryption, asymmetric encryption, hashing, digital signatures, key derivation, message authentication codes, and X.509 certificates.

## Architecture

```
crypto/graphy/
├── __init__.py       # 46 re-exports across 7 submodules
├── symmetric.py      # AES-GCM, ChaCha20-Poly1305 encrypt/decrypt
├── asymmetric.py     # RSA, EC, Ed25519, X25519 key generation and encryption
├── hashing.py        # SHA-256, SHA-512, SHA3-256, BLAKE2b, MD5
├── signatures.py     # ECDSA, Ed25519, RSA-PSS sign/verify
├── kdf.py            # PBKDF2, scrypt, Argon2id, HKDF
├── mac.py            # HMAC-SHA256, CMAC, Poly1305
└── certificates.py   # Self-signed certs, CSR, chain validation
```

## Key Classes and Functions

### symmetric.py

| Name | Kind | Description |
|------|------|-------------|
| `CipherResult` | dataclass | Encryption result holding ciphertext, nonce, and tag |
| `encrypt_aes_gcm` | function | AES-256-GCM authenticated encryption |
| `decrypt_aes_gcm` | function | AES-256-GCM authenticated decryption |
| `encrypt_chacha20` | function | ChaCha20-Poly1305 authenticated encryption |
| `decrypt_chacha20` | function | ChaCha20-Poly1305 authenticated decryption |
| `generate_symmetric_key` | function | Generate a random symmetric key of specified length |

### asymmetric.py

| Name | Kind | Description |
|------|------|-------------|
| `KeyPair` | dataclass | Container for public/private key pair |
| `generate_rsa_keypair` | function | Generate an RSA key pair (2048/4096 bit) |
| `generate_ec_keypair` | function | Generate an elliptic curve key pair (P-256/P-384) |
| `generate_ed25519_keypair` | function | Generate an Ed25519 signing key pair |
| `generate_x25519_keypair` | function | Generate an X25519 key-agreement key pair |
| `rsa_encrypt` | function | RSA-OAEP encryption |
| `rsa_decrypt` | function | RSA-OAEP decryption |
| `load_private_key` | function | Deserialize a private key from PEM/DER bytes |
| `load_public_key` | function | Deserialize a public key from PEM/DER bytes |
| `serialize_private_key` | function | Serialize a private key to PEM bytes |
| `serialize_public_key` | function | Serialize a public key to PEM bytes |

### hashing.py

| Name | Kind | Description |
|------|------|-------------|
| `HashAlgorithm` | enum | Supported hash algorithms (SHA256, SHA512, SHA3_256, BLAKE2B, MD5) |
| `hash_data` | function | Hash data with a specified algorithm |
| `hash_sha256` | function | SHA-256 hash |
| `hash_sha512` | function | SHA-512 hash |
| `hash_sha3_256` | function | SHA3-256 hash |
| `hash_blake2b` | function | BLAKE2b hash |
| `hash_md5` | function | MD5 hash (not for security use) |
| `verify_hash` | function | Constant-time hash verification |

### signatures.py

| Name | Kind | Description |
|------|------|-------------|
| `sign_ecdsa` | function | ECDSA signature creation |
| `verify_ecdsa` | function | ECDSA signature verification |
| `sign_ed25519` | function | Ed25519 signature creation |
| `verify_ed25519` | function | Ed25519 signature verification |
| `sign_rsa_pss` | function | RSA-PSS signature creation |
| `verify_rsa_pss` | function | RSA-PSS signature verification |

### kdf.py

| Name | Kind | Description |
|------|------|-------------|
| `DerivedKey` | dataclass | KDF result holding derived key bytes and salt |
| `derive_pbkdf2` | function | PBKDF2-HMAC-SHA256 key derivation |
| `derive_scrypt` | function | scrypt key derivation |
| `derive_argon2id` | function | Argon2id key derivation |
| `derive_hkdf` | function | HKDF-SHA256 key derivation |

### mac.py

| Name | Kind | Description |
|------|------|-------------|
| `compute_hmac_sha256` | function | Compute HMAC-SHA256 tag |
| `verify_hmac_sha256` | function | Constant-time HMAC-SHA256 verification |
| `compute_cmac` | function | Compute AES-CMAC tag |
| `compute_poly1305` | function | Compute Poly1305 tag |

### certificates.py

| Name | Kind | Description |
|------|------|-------------|
| `ValidationResult` | dataclass | Certificate chain validation result |
| `generate_self_signed_cert` | function | Generate a self-signed X.509 certificate |
| `generate_csr` | function | Generate a Certificate Signing Request |
| `load_certificate_pem` | function | Load an X.509 certificate from PEM |
| `export_certificate_pem` | function | Export an X.509 certificate to PEM |
| `validate_certificate_chain` | function | Validate a certificate chain against a trust store |

## Dependencies

- `cryptography` library (Fernet, hazmat primitives)
- Python `hashlib`, `hmac`, `os` (standard library)

## Constraints

- AES-GCM nonces are 12 bytes, generated randomly per encryption call.
- RSA key sizes must be at least 2048 bits.
- `hash_md5` is provided for legacy compatibility; not suitable for security.

## Error Handling

| Error | When |
|-------|------|
| `ValueError` | Invalid key size, unsupported algorithm, decryption failure |
| `InvalidSignature` | Signature verification failure (from `cryptography` library) |
| `InvalidTag` | AEAD authentication tag mismatch |

## Navigation

- **Parent**: [crypto/SPEC.md](../SPEC.md)
- **Siblings**: [AGENTS.md](AGENTS.md), [README.md](README.md), [PAI.md](PAI.md)
