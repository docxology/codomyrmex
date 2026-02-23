# Crypto Tests — Agent Responsibilities

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Agent Test Ownership

### Engineer Agent

**Responsibility**: Implement and maintain all test files.

| Test File | Focus |
|---|---|
| test_graphy_symmetric.py | AES-GCM, ChaCha20-Poly1305 round-trip, error handling |
| test_graphy_asymmetric.py | RSA, Ed25519, X25519, ECC key generation and operations |
| test_graphy_hashing.py | Hash correctness against known vectors |
| test_graphy_signatures.py | Sign/verify round-trip, invalid signature rejection |
| test_graphy_kdf.py | KDF output against RFC vectors, parameter validation |
| test_graphy_mac.py | MAC computation and constant-time verification |
| test_graphy_certs.py | Certificate generation, chain verification |
| test_currency.py | Wallet generation, address derivation, transaction signing |
| test_encoding.py | Round-trip encoding, malformed input rejection |
| test_protocols.py | Key exchange, secret sharing, ZKP correctness |
| test_random.py | CSPRNG output quality, NIST test execution |
| test_steganography.py | Embed/extract round-trip, detection methods |
| test_analysis.py | Entropy calculation, strength assessment |

### QATester Agent

**Responsibility**: Execute test suite and validate results.

| Activity | Command |
|---|---|
| Run all crypto tests | `uv run pytest src/codomyrmex/tests/unit/crypto/ -v` |
| Run with coverage | `uv run pytest src/codomyrmex/tests/unit/crypto/ --cov=src/codomyrmex/crypto` |
| Run security tests | `uv run pytest -m "crypto and security"` |
| Run fast tests only | `uv run pytest -m "crypto and not slow"` |
| Validate coverage targets | Compare report against SPEC.md thresholds |

### Architect Agent

**Responsibility**: Review test architecture and coverage strategy.

- Verify tests cover all API surfaces defined in API_SPECIFICATION.md.
- Ensure test categories (correctness, error, security, performance) are balanced.
- Review fixture design for appropriate isolation.
- Validate that test vectors reference authoritative sources.

### Security Agent

**Responsibility**: Audit security-specific tests.

- Verify nonce uniqueness tests use sufficient sample sizes.
- Confirm constant-time comparison tests are meaningful.
- Validate that error paths do not leak sensitive information.
- Ensure deprecated algorithm tests include appropriate warnings.
