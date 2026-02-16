# Crypto Module — Test Suite

**Version**: v0.1.0 | **Last Updated**: February 2026

## Overview

Unit and integration tests for the `codomyrmex.crypto` module covering all 7 submodules: graphy, currency, analysis, steganography, encoding, random, and protocols.

## Test Structure

```
tests/unit/crypto/
    conftest.py              # Shared fixtures (keys, plaintext, temp images)
    test_graphy_symmetric.py # AES-GCM, ChaCha20-Poly1305
    test_graphy_asymmetric.py # RSA, Ed25519, X25519, ECC
    test_graphy_hashing.py   # SHA-256/3/512, BLAKE2b, MD5
    test_graphy_signatures.py # ECDSA, EdDSA, RSA-PSS
    test_graphy_kdf.py       # PBKDF2, scrypt, Argon2id, HKDF
    test_graphy_mac.py       # HMAC, Poly1305, CMAC
    test_graphy_certs.py     # X.509 certificates
    test_currency.py         # Wallets, blockchain, transactions, addresses, tokens
    test_analysis.py         # Entropy, frequency, strength, classical breaking
    test_steganography.py    # Image LSB, text steg, detection
    test_encoding.py         # Base64/58/32, hex, PEM
    test_random.py           # CSPRNG, NIST tests
    test_protocols.py        # Key exchange, secret sharing, ZKP
```

## Running Tests

```bash
# All crypto tests
uv run pytest src/codomyrmex/tests/unit/crypto/

# Specific submodule
uv run pytest src/codomyrmex/tests/unit/crypto/test_graphy_symmetric.py

# By marker
uv run pytest -m crypto
uv run pytest -m "crypto and not slow"

# With coverage
uv run pytest src/codomyrmex/tests/unit/crypto/ --cov=src/codomyrmex/crypto --cov-report=html
```

## Fixtures (conftest.py)

| Fixture | Description |
|---|---|
| `symmetric_key` | 32-byte random AES key |
| `sample_plaintext` | Standard test plaintext bytes |
| `rsa_keypair` | RSA-2048 private/public key tuple |
| `ed25519_keypair` | Ed25519 private/public key tuple |
| `ec_keypair` | SECP256R1 private/public key tuple |
| `temp_image` | 100x100 red PNG image file path |
| `known_entropy_data` | 1024 zero bytes (entropy = 0.0) |

## Test Markers

- `@pytest.mark.crypto` — All crypto tests
- `@pytest.mark.unit` — Fast unit tests
- `@pytest.mark.slow` — Performance and large-data tests
- `@pytest.mark.security` — Security-sensitive validation tests

## Coverage Targets

See [SPEC.md](SPEC.md) for detailed coverage targets per submodule.
