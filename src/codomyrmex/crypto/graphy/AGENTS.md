# crypto/graphy -- Agent Context

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Module Summary

The `crypto/graphy` submodule is a comprehensive cryptography primitives library covering symmetric encryption (AES-GCM, ChaCha20-Poly1305), asymmetric encryption (RSA, EC, Ed25519, X25519), hashing (SHA-256/512, SHA3, BLAKE2b, MD5), digital signatures (RSA-PSS, ECDSA, Ed25519), key derivation (PBKDF2, HKDF, scrypt, Argon2id), MACs (HMAC-SHA256, CMAC, Poly1305), and X.509 certificate operations.

## When to Use This Module

- You need production-grade symmetric encryption with AES-GCM or ChaCha20-Poly1305
- You need to generate or load RSA, EC, Ed25519, or X25519 key pairs
- You need to hash data with modern algorithms (SHA-3, BLAKE2b) or legacy (MD5, SHA-256)
- You need digital signatures (ECDSA, Ed25519, RSA-PSS)
- You need key derivation with Argon2id, scrypt, PBKDF2, or HKDF
- You need MAC computation (HMAC-SHA256, CMAC, Poly1305)
- You need to generate self-signed certificates, CSRs, or validate certificate chains

## Exports (by category)

**Symmetric**: `CipherResult`, `encrypt_aes_gcm`, `decrypt_aes_gcm`, `encrypt_chacha20`, `decrypt_chacha20`, `generate_symmetric_key`

**Asymmetric**: `KeyPair`, `generate_rsa_keypair`, `generate_ec_keypair`, `generate_ed25519_keypair`, `generate_x25519_keypair`, `load_private_key`, `load_public_key`, `rsa_encrypt`, `rsa_decrypt`, `serialize_private_key`, `serialize_public_key`

**Hashing**: `HashAlgorithm`, `hash_data`, `hash_sha256`, `hash_sha512`, `hash_sha3_256`, `hash_blake2b`, `hash_md5`, `verify_hash`

**Signatures**: `sign_rsa_pss`, `verify_rsa_pss`, `sign_ecdsa`, `verify_ecdsa`, `sign_ed25519`, `verify_ed25519`

**KDF**: `DerivedKey`, `derive_pbkdf2`, `derive_hkdf`, `derive_scrypt`, `derive_argon2id`

**MAC**: `compute_hmac_sha256`, `verify_hmac_sha256`, `compute_cmac`, `compute_poly1305`

**Certificates**: `ValidationResult`, `generate_self_signed_cert`, `generate_csr`, `load_certificate_pem`, `export_certificate_pem`, `validate_certificate_chain`

## Example Agent Usage

```python
from codomyrmex.crypto.graphy import (
    generate_symmetric_key, encrypt_aes_gcm, decrypt_aes_gcm,
    generate_ed25519_keypair, sign_ed25519, verify_ed25519,
    hash_sha256, derive_argon2id,
)

# Symmetric encryption
key = generate_symmetric_key(256)
result = encrypt_aes_gcm(b"secret", key)
plaintext = decrypt_aes_gcm(result.ciphertext, key, result.nonce, result.tag)

# Digital signatures
kp = generate_ed25519_keypair()
sig = sign_ed25519(b"message", kp.private_key)
assert verify_ed25519(b"message", sig, kp.public_key)

# Hashing and KDF
digest = hash_sha256(b"data")
dk = derive_argon2id(b"password", salt=b"random-salt")
```

## Constraints

- All functions use the `cryptography` library; it must be installed.
- `hash_md5` is provided for compatibility; MD5 is not collision-resistant.
- Certificate validation requires a trust chain; self-signed certs validate against themselves.

## Relationship to Other Modules

| Module | Relationship |
|--------|-------------|
| `encryption.algorithms` | Higher-level AES-GCM wrapper; uses same underlying crypto |
| `encryption.keys` | Key management and HMAC utilities |
| `crypto.protocols` | Consumes key pairs for key exchange and zero-knowledge proofs |
| `crypto.encoding` | Encode/decode keys and ciphertext for transport |
