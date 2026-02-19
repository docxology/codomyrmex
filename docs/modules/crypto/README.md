# Crypto Module

**Version**: v0.1.7 | **Status**: Active | **Last Updated**: February 2026

## Overview

The Crypto module provides comprehensive cryptographic operations for the Codomyrmex platform. It is organized into seven self-contained submodules covering the full spectrum of modern cryptography: primitives, cryptocurrency, cryptanalysis, steganography, encoding, randomness, and protocols.

All implementations use established libraries (`cryptography`, `pycryptodome`, `hashlib`) rather than hand-rolled algorithms. Keys are always generated from CSPRNGs. No secrets are hardcoded.

## Submodules

| Submodule | Description |
|---|---|
| **graphy/** | Cryptography primitives: symmetric ciphers (AES-GCM, ChaCha20-Poly1305), asymmetric (RSA, Ed25519, X25519, ECC), hashing (SHA-256/3/512, BLAKE2b), digital signatures (ECDSA, EdDSA, RSA-PSS), KDFs (PBKDF2, scrypt, Argon2id, HKDF), MACs (HMAC, Poly1305, CMAC), X.509 certificates |
| **currency/** | Cryptocurrency operations: BIP-32/39/44 HD wallets, blockchain and Merkle trees, transaction construction, Bitcoin/Ethereum address generation, ERC-20 token interfaces |
| **analysis/** | Cryptanalysis tools: Shannon entropy measurement, frequency analysis, password/key strength assessment, classical cipher breaking (Caesar, Vigenere) |
| **steganography/** | Data hiding techniques: image LSB embedding/extraction, zero-width character text steganography, statistical detection methods |
| **encoding/** | Crypto-related encodings: Base64, Base58 (Bitcoin), Base32, hexadecimal, PEM format parsing and generation |
| **random/** | Cryptographic randomness: CSPRNG wrappers, NIST SP 800-22 statistical test suite for randomness quality validation |
| **protocols/** | Cryptographic protocols: Diffie-Hellman and ECDH key exchange, Shamir secret sharing, zero-knowledge proofs (Schnorr, Pedersen commitment) |

## Installation

```bash
uv sync --extra crypto
```

This installs all required dependencies including `cryptography`, `pycryptodome`, `Pillow` (for steganography), and `mnemonic` (for BIP-39).

## Quick Start

### Symmetric Encryption (graphy)

```python
from codomyrmex.crypto.graphy.symmetric import encrypt_aes_gcm, decrypt_aes_gcm
import os

key = os.urandom(32)
ciphertext, nonce, tag = encrypt_aes_gcm(b"secret message", key)
plaintext = decrypt_aes_gcm(ciphertext, key, nonce, tag)
```

### Hashing (graphy)

```python
from codomyrmex.crypto.graphy.hashing import hash_data
digest = hash_data(b"hello world", "sha256")
```

### Key Derivation (graphy)

```python
from codomyrmex.crypto.graphy.kdf import derive_argon2id
derived_key = derive_argon2id(b"password", salt=os.urandom(16))
```

### Entropy Analysis (analysis)

```python
from codomyrmex.crypto.analysis.entropy import shannon_entropy
entropy = shannon_entropy(b"analyze this data")
```

### Encoding (encoding)

```python
from codomyrmex.crypto.encoding.base_encodings import encode_base64, decode_base64
encoded = encode_base64(b"data")
decoded = decode_base64(encoded)
```

### Random Generation (random)

```python
from codomyrmex.crypto.random.csprng import generate_random_bytes
secure_bytes = generate_random_bytes(32)
```

### Key Exchange (protocols)

```python
from codomyrmex.crypto.protocols.key_exchange import ecdh_keypair, ecdh_shared_secret
private_a, public_a = ecdh_keypair()
private_b, public_b = ecdh_keypair()
shared = ecdh_shared_secret(private_a, public_b)
```

## Security Considerations

- All symmetric keys are 256-bit minimum. AES uses GCM mode for authenticated encryption.
- RSA keys are 4096-bit by default. Asymmetric operations use OAEP padding.
- MD5 is available for legacy compatibility but marked deprecated. SHA-1 is not included.
- Password hashing defaults to Argon2id with OWASP-recommended parameters.
- CSPRNG uses `os.urandom()` backed by the OS entropy pool.
- See [SECURITY.md](SECURITY.md) for full security analysis.

## Architecture

The crypto module follows the Codomyrmex module conventions:

- Each submodule is self-contained with its own `__init__.py`
- No cross-dependencies between submodules (graphy does not import from currency, etc.)
- All exceptions inherit from `CryptoError` (see `exceptions.py`)
- CLI commands registered via `cli_commands()` in the top-level `__init__.py`
- Dependency on the Foundation layer only (`logging_monitoring`, `environment_setup`)

## CLI Commands

```bash
codomyrmex crypto:status       # Check submodule availability
codomyrmex crypto:algorithms   # List supported algorithms
codomyrmex crypto:hash         # Quick hash computation
```
