# Crypto Module — Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Supported Algorithms and Parameters

### Symmetric Ciphers

| Algorithm | Key Size | Mode | Nonce Size | Tag Size | Security Level |
|---|---|---|---|---|---|
| AES-256-GCM | 256 bits | GCM (AEAD) | 96 bits | 128 bits | 128-bit security |
| ChaCha20-Poly1305 | 256 bits | AEAD | 96 bits | 128 bits | 128-bit security |

### Asymmetric Algorithms

| Algorithm | Key Size | Use Case | Security Level |
|---|---|---|---|
| RSA-4096 | 4096 bits | Encryption, signatures | ~140-bit security |
| Ed25519 | 256 bits | Signatures | ~128-bit security |
| X25519 | 256 bits | Key exchange | ~128-bit security |
| SECP256R1 (P-256) | 256 bits | Signatures, key agreement | ~128-bit security |

### Hash Functions

| Algorithm | Output Size | Status | Use Case |
|---|---|---|---|
| SHA-256 | 256 bits | Recommended | General purpose |
| SHA-3-256 | 256 bits | Recommended | Alternative to SHA-2 |
| SHA-512 | 512 bits | Recommended | High-security hashing |
| BLAKE2b | Up to 512 bits | Recommended | High-performance hashing |
| MD5 | 128 bits | **Deprecated** | Legacy compatibility only |

**Note**: SHA-1 is intentionally excluded. It is cryptographically broken for collision resistance and should not be used.

### Digital Signatures

| Algorithm | Key Type | Hash | Security Level |
|---|---|---|---|
| ECDSA | SECP256R1 | SHA-256 | ~128-bit security |
| EdDSA (Ed25519) | Ed25519 | SHA-512 (internal) | ~128-bit security |
| RSA-PSS | RSA-4096 | SHA-256 | ~140-bit security |

### Key Derivation Functions

| Algorithm | Parameters | Recommended Use |
|---|---|---|
| PBKDF2-HMAC-SHA256 | iterations=600000, key_length=32 | Legacy password hashing |
| scrypt | N=2^20, r=8, p=1 | Memory-hard password hashing |
| Argon2id | time=3, memory=65536KB, parallelism=4 | **Recommended** password hashing |
| HKDF-SHA256 | Variable length, optional salt/info | Key expansion from existing key material |

Argon2id parameters follow OWASP 2024 recommendations.

### Message Authentication Codes

| Algorithm | Key Size | Tag Size | Notes |
|---|---|---|---|
| HMAC-SHA256 | >= 256 bits | 256 bits | General purpose |
| Poly1305 | 256 bits | 128 bits | Used with ChaCha20 |
| AES-CMAC | 128/256 bits | 128 bits | Block cipher based |

### Encoding Formats

| Format | Alphabet Size | Efficiency | Use Case |
|---|---|---|---|
| Base64 | 64 chars | 75% | General binary-to-text |
| Base64url | 64 chars | 75% | URL-safe encoding (RFC 4648) |
| Base58 | 58 chars | ~73% | Bitcoin addresses |
| Base32 | 32 chars | 62.5% | Case-insensitive encoding |
| Hex | 16 chars | 50% | Debug/display |
| PEM | Base64 + headers | ~75% | Certificate/key serialization |

### Cryptographic Protocols

| Protocol | Type | Parameters | Security Guarantee |
|---|---|---|---|
| Diffie-Hellman | Key exchange | 2048-bit modulus | Computational DH assumption |
| ECDH (X25519) | Key exchange | Curve25519 | Computational DH assumption |
| Shamir Secret Sharing | Secret sharing | (t, n) threshold | Information-theoretic |
| Schnorr ZKP | Zero-knowledge proof | Discrete log groups | Honest-verifier ZK |
| Pedersen Commitment | Commitment scheme | Two generators (g, h) | Computationally hiding, perfectly binding |

### Cryptocurrency Standards

| Standard | Description |
|---|---|
| BIP-32 | Hierarchical Deterministic Wallets |
| BIP-39 | Mnemonic code for generating deterministic keys |
| BIP-44 | Multi-account hierarchy for deterministic wallets |
| P2PKH | Pay-to-Public-Key-Hash (Bitcoin address type) |
| EIP-55 | Mixed-case checksum address encoding (Ethereum) |
| ERC-20 | Token standard interface |

### NIST SP 800-22 Tests

| Test | Purpose | Minimum Data |
|---|---|---|
| Frequency (Monobit) | Overall balance of 0s and 1s | 100 bits |
| Runs | Oscillation of 0/1 sequences | 100 bits |
| Block Frequency | Balance within M-bit blocks | 100 bits |

## Security Levels Summary

All algorithms provide a minimum of 128-bit security level, with the exception of:

- MD5 (deprecated, collision-broken, included for legacy compatibility only)
- RSA-4096 provides approximately 140-bit security

## Dependencies

| Package | Version | Purpose |
|---|---|---|
| `cryptography` | >= 42.0 | Core crypto primitives |
| `pycryptodome` | >= 3.20 | Additional ciphers, Shamir sharing |
| `Pillow` | >= 10.0 | Image steganography |
| `mnemonic` | >= 0.20 | BIP-39 mnemonic generation |
| `argon2-cffi` | >= 23.1 | Argon2id KDF |

## Interface Contracts

### Symmetric Cryptography (`graphy.symmetric`)

```python
def encrypt_aes_gcm(data: bytes, key: bytes, associated_data: bytes | None = None) -> CipherResult
def decrypt_aes_gcm(encrypted_data: bytes, key: bytes, associated_data: bytes | None = None) -> bytes
def encrypt_chacha20(data: bytes, key: bytes, nonce: bytes | None = None) -> CipherResult
def decrypt_chacha20(encrypted_data: bytes, key: bytes, nonce: bytes) -> bytes
def generate_symmetric_key(algorithm: str = "aes-256") -> bytes
```

### Asymmetric Cryptography (`graphy.asymmetric`)

```python
def generate_rsa_keypair(key_size: int = 4096) -> KeyPair
def generate_ec_keypair(curve_name: str = "secp256r1") -> KeyPair
def generate_ed25519_keypair() -> KeyPair
def rsa_encrypt(data: bytes, public_key: bytes) -> bytes
def rsa_decrypt(encrypted_data: bytes, private_key: bytes) -> bytes
```

### Hashing and Signatures (`graphy.hashing`, `graphy.signatures`)

```python
def hash_data(data: bytes, algorithm: str = "sha256") -> str
def verify_hash(data: bytes, hash_value: str, algorithm: str = "sha256") -> bool
def sign_rsa_pss(data: bytes, private_key: bytes) -> bytes
def verify_rsa_pss(data: bytes, signature: bytes, public_key: bytes) -> bool
def sign_ecdsa(data: bytes, private_key: bytes) -> bytes
def verify_ecdsa(data: bytes, signature: bytes, public_key: bytes) -> bool
```

### Key Derivation (`graphy.kdf`)

```python
def derive_argon2id(password: bytes, salt: bytes | None = None, ...) -> DerivedKey
def derive_pbkdf2(password: bytes, salt: bytes | None = None, ...) -> DerivedKey
def derive_hkdf(input_key: bytes, info: bytes, salt: bytes | None = None, ...) -> bytes
```

## Navigation

- **Parent**: [codomyrmex](../AGENTS.md)
- **Related**: [encryption](../encryption/SPEC.md), [security](../security/SPEC.md)
